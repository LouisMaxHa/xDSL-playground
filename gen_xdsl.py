#!/usr/bin/env python3

import subprocess
import sys
from pathlib import Path

from xdsl.builder import Builder
from xdsl.context import Context
from xdsl.dialects import arith, builtin, llvm, memref, ptr
from xdsl.dialects.builtin import (
    IndexType,
    IntegerAttr,
    IntegerType,
    MemRefType,
    ModuleOp,
    UnitAttr,
)
from xdsl.dialects.func import FuncOp, ReturnOp
from xdsl.printer import Printer
from xdsl.rewriter import InsertPoint
from xdsl.transforms.canonicalize import CanonicalizePass
from xdsl.transforms.convert_memref_to_ptr import ConvertMemRefToPtr
from xdsl.transforms.convert_ptr_to_llvm import (
    ConvertPtrToLLVMPass,
)
from xdsl.transforms.reconcile_unrealized_casts import ReconcileUnrealizedCastsPass


# ──────────── Utils ────────────
def run(cmd: list[str]):
    print(" ".join(cmd))
    try:
        subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True
        ).stdout
    except subprocess.CalledProcessError as exc:
        print()
        print(f"Error when running {cmd} :", file=sys.stderr)
        print(exc.stderr, file=sys.stderr)
        exit(1)


def display(path: Path, text: str):
    print()
    print("──────────── " + text)
    print(path.read_text())


# ──────────── Passes config ────────────
XDSL_OPT_PASSES = [
    ConvertMemRefToPtr,
    # Simplifies ptr.to_ptr(ptr.from_ptr(p)) → p after ConvertMemRefToPtr.
    # Required when memref views are backed by llvm.alloca via ptr.from_ptr.
    CanonicalizePass,
    # ConvertPtrTypeOffsetsPass,
    ConvertPtrToLLVMPass,
    ReconcileUnrealizedCastsPass,
]

MLIR_OPT_OPTIMIZE_PASSES = [
    # "--loop-invariant-code-motion",
    # "--cse",
    # "--canonicalize",
    # "--symbol-dce",
    # "--mem2reg",
    # "--expand-strided-metadata",
    # "--normalize-memrefs",
    # "--memref-expand",
    # "--fold-memref-alias-ops",
]

# Will be concatenate into a --pass-pipeline=builtin.module(...)
MLIR_OPT_LOWER_TO_LLVM = [
    "lower-affine",
    "convert-scf-to-cf",
    "expand-strided-metadata",
    "convert-to-llvm",
    "convert-cf-to-llvm",
    "convert-arith-to-llvm",
    "convert-index-to-llvm",
    "convert-func-to-llvm",
    "reconcile-unrealized-casts",
]


# ──────────── Main ────────────
def main():
    HERE = Path(__file__).resolve().parent
    BUILD = HERE / "build"
    BUILD.mkdir(exist_ok=True)

    path_xdsl: Path = BUILD / "xdsl.mlir"
    path_mlir: Path = BUILD / "raw.mlir"
    path_mlir_opt: Path = BUILD / "optimized.mlir"
    path_llvm_mlir: Path = BUILD / "llvm.mlir"
    path_llvm_ir: Path = BUILD / "gen.ll"
    path_obj: Path = BUILD / "gen.o"
    path_out: Path = HERE / "gen.out"

    # Create module
    module = ModuleOp([])
    builder_module = Builder(InsertPoint.at_end(module.body.block))

    # Add function
    func = FuncOp("xdsl_main", ([IntegerType(64)], [IntegerType(64)]))
    func.attributes["llvm.emit_c_interface"] = UnitAttr()
    _ = builder_module.insert(func)
    builder = Builder(InsertPoint.at_end(func.body.block))
    arg = func.args[0]

    print(
        """Enter your choice:
0) i64 -> ptr.ptr (ok)
1) i64 -> memeref.alloca + ptr.from_ptr -> memref<i64> -> ptr.ptr (error)
2) i64 -> llvm.alloca + ptr.from_ptr -> memref<i64> -> ptr.ptr (ok)"""
    )
    choice = input("> ")
    addr_local = None

    if choice in ("0", ""):
        # Take directly the arg
        addr_local = arg


    if choice == "1":
        # Alloca, store to alloca, load from alloca

        # Alloc addrAlloca (memref<i64>)
        addr_alloca = builder.insert(
            memref.AllocaOp.get(IntegerType(64), shape=[])
        ).memref
        addr_alloca.name_hint = "addrAlloca"

        # Store addr into addrAlloca
        _ = builder.insert(
            memref.StoreOp.get(arg, addr_alloca, [])
        )

        # Load it back to addrLocal
        addr_local = builder.insert(
            memref.LoadOp.get(addr_alloca, [])
        ).results[0]
        addr_local.name_hint = "addrLocal"


    if choice == "2":
        # llvm.alloca requires a signless integer size (not index)
        size_one = builder.insert(
            llvm.ConstantOp(IntegerAttr(1, IntegerType(32)), IntegerType(32))
        ).result
        size_one.name_hint = "c1"

        # llvm.alloca
        addr_alloca_llvm = builder.insert(
            llvm.AllocaOp(size_one, IntegerType(64))
        ).res
        addr_alloca_llvm.name_hint = "llvmAlloca"

        # llvm.ptr → ptr_xdsl.ptr
        addr_alloca_xptr = builder.insert(
            builtin.UnrealizedConversionCastOp.get(
                [addr_alloca_llvm], [ptr.PtrType()]
            )
        ).results[0]
        addr_alloca_xptr.name_hint = "addrAllocaXPtr"

        # Expose as memref<i64>
        addr_alloca = builder.insert(
            ptr.FromPtrOp(addr_alloca_xptr, MemRefType(IntegerType(64), []))
        ).results[0]
        addr_alloca.name_hint = "addrAlloca"

        # Store arg into addrAlloca
        _ = builder.insert(
            memref.StoreOp.get(arg, addr_alloca, [])
        )

        # Load it back to addrLocal
        addr_local = builder.insert(
            memref.LoadOp.get(addr_alloca, [])
        ).results[0]
        addr_local.name_hint = "addrLocal"

    assert addr_local is not None

    # i64 addr -> llvm.ptr
    ptr_llvm = builder.insert(
        llvm.IntToPtrOp(input=addr_local)
    ).results[0]
    ptr_llvm.name_hint = "llvmPtr"

    # llvm.ptr -> ptr.ptr
    ptr_ptr = builder.insert(
        builtin.UnrealizedConversionCastOp.get([ptr_llvm], [ptr.PtrType()])
    ).results[0]
    ptr_ptr.name_hint = "ptrPtr"

    # ptr.ptr -> memref<i64>
    deref = builder.insert(
        ptr.FromPtrOp(ptr_ptr, MemRefType(IntegerType(64), []))
    ).results[0]
    deref.name_hint = "deref"

    #   memref<i64> -> i64
    loaded = builder.insert(
        memref.LoadOp.get(deref, [])
    ).results[0]
    loaded.name_hint = "loaded"

    # return i64
    _ = builder.insert(ReturnOp(loaded))
    func.update_function_type()



    # ──────────── Compilation pipeline
    # xDSL -> MLIR
    with path_xdsl.open("w", encoding="utf-8") as f:
        Printer(stream=f).print_op(module)
    display(path_xdsl, "xDSL mlir")

    # xDSL -> xDSL
    ctx = Context()
    for passe in XDSL_OPT_PASSES:
        passe().apply(ctx, module)
        print(f"\n──────────── xDSL after {passe.__name__} passe")
        Printer().print_op(module)
        print()

    # xDSL -> MLIR
    with path_mlir.open("w", encoding="utf-8") as f:
        Printer(stream=f).print_op(module)
    display(path_mlir, "Mlir")



    # MLIR -> MLIR (optimize)
    run([
        "mlir-opt", str(path_mlir),
        *MLIR_OPT_OPTIMIZE_PASSES,
        "-o", str(path_mlir_opt)
    ])
    display(path_mlir, "optimized mlir")


    # MLIR -> LLVM dialect of MLIR
    run([
        "mlir-opt",
        f"--pass-pipeline=builtin.module({','.join(MLIR_OPT_LOWER_TO_LLVM)})",
        str(path_mlir_opt),
        "-o", str(path_llvm_mlir)
    ])
    display(path_llvm_mlir, "Llvm mlir")


    # MLIR -> LLVM
    run([
        "mlir-translate", "--mlir-to-llvmir", str(path_llvm_mlir),
        "-o", str(path_llvm_ir)
    ])
    display(path_llvm_ir, "llvm")


    # LLVM -> librairie
    run([
        "llc", "-O2", "-filetype=obj",
        "-relocation-model=pic", str(path_llvm_ir),
        "-o", str(path_obj)
    ])

    # librairie + caller.cpp -> runnable
    run([
        "clang++", str(path_obj), str(HERE / "caller.cpp"),
        "-o", str(path_out)
    ])


if __name__ == "__main__":
    main()
