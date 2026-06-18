# Some tests with xDSL


```
git clone https://github.com/LouisMaxHa/xDSL-playground
cd xDSL-playground

python3 -m venv .venv
uv run python gen_xdsl.py

> Enter your choice:
> 0) i64   -> ptr.ptr (ok)
> 1) i64 -> memref.alloca -(error)> i64 -> ptr.ptr
```

The goal of this project is to create a function that takes a pointer to an integer and returns its value.
We'll use a C++ program (`caller.cpp`) that will call this external function.
The purpose of this is to create a proof of concept (PoC) for more advanced functions.

This short demo is to test the use of the ptr dialect with xDSL.
The first function works, but the second one has a problem during lowering; below is an excerpt from the IR that causes the issue. It seems to be caused by the alloca of a i64 using memref.


### xDSL generated
```mlir
// Store
%addrAlloca = memref.alloca() : memref<i64>
memref.store %0, %addrAlloca[] : memref<i64>
// Load
%addrLocal = memref.load %addrAlloca[] : memref<i64>
```

### xDSL after ConvertMemRefToPtr pass
```mlir
// Store
%addrAlloca = memref.alloca() : memref<i64>
%addrAlloca_1 = ptr_xdsl.to_ptr %addrAlloca : memref<i64> -> !ptr_xdsl.ptr
ptr_xdsl.store %0, %addrAlloca_1 : i64, !ptr_xdsl.ptr
// Load
%addrAlloca_2 = ptr_xdsl.to_ptr %addrAlloca : memref<i64> -> !ptr_xdsl.ptr
%addrLocal = ptr_xdsl.load %addrAlloca_2 : !ptr_xdsl.ptr -> i64
```

### xDSL after ConvertPtrToLLVMPass pass
```mlir
// Store
%addrAlloca = memref.alloca() : memref<i64>
%1 = builtin.unrealized_conversion_cast %addrAlloca : memref<i64> to !llvm.ptr
"llvm.store"(%0, %1) <{ordering = 0 : i64}> : (i64, !llvm.ptr) -> ()
// Load
%addrLocal = builtin.unrealized_conversion_cast %addrAlloca : memref<i64> to !llvm.ptr
```

> .venv/lib64/python3.14/site-packages/xdsl/transforms/reconcile_unrealized_casts.py:77:
> UserWarning: Unable to remove cast UnrealizedConversionCastOp(
>   %0 = builtin.unrealized_conversion_cast %addrAlloca : memref<i64> to !llvm.ptr
> )
> because it is not unifiable with its uses
