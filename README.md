# xDSL, ptr.ptr and memref.alloca

This repo aims to analyze and propose a solution to improve the use of the `xdsl_ptr` dialect and its compatibility with `memref.alloca` and the `ptr` dialect.

```
git clone https://github.com/LouisMaxHa/xDSL-playground
cd xDSL-playground

uv venv
source .venv/bin/activate
uv pip install xdsl
uv run python gen_xdsl.py

Enter your choice:
0) i64 -> ptr.ptr (ok)
1) i64 -> memref.alloca + ptr.from_ptr -> memref<i64> -> ptr.ptr (error)
2) i64 -> llvm.alloca + ptr.from_ptr -> memref<i64> -> ptr.ptr (ok)
> 
```

The goal of this project is to create a function that takes a pointer to an integer and returns its value.
We'll use a C++ program (`caller.cpp`) that will call this external function.
The purpose of this is to create a proof of concept (PoC) for more advanced functions.

This short demo is to test the use of the ptr dialect with xDSL.
The first function works, but the second one has a problem during lowering; below is an excerpt from the IR that causes the issue. It seems to be caused by the alloca of an i64 using memref.

### What's wrong?

1) We allocate `memref<i64>`
```mlir
%ssaAlloca = memref.alloca() : memref<i64>
memref.store %0, %ssaAlloca[] : memref<i64>
```
2) We use the xDSL pass `ConvertMemRefToPtr`
Since `memref.alloca` lowering is not implemented, this memref occurrence is unchanged but the store is correctly lowered to `ptr_xdsl.store`.
```mlir
%ssaAlloca = memref.alloca() : memref<i64>
%ssaAlloca_1 = ptr_xdsl.to_ptr %ssaAlloca : memref<i64> -> !ptr_xdsl.ptr
ptr_xdsl.store %0, %ssaAlloca_1 : i64, !ptr_xdsl.ptr
```

3) We use the xDSL pass `ConvertPtrToLLVMPass`
To lower `ptr_xdsl.store` to `llvm.store`, we need to force the conversion of `ssaAlloca : memref<i64>` to `llvm.ptr`, thus introducing a `builtin.unrealized_conversion_cast`. 
```mlir
%ssaAlloca = memref.alloca() : memref<i64>
%1 = builtin.unrealized_conversion_cast %ssaAlloca : memref<i64> to !llvm.ptr
"llvm.store"(%0, %1) <{ordering = 0 : i64}> : (i64, !llvm.ptr) -> ()
```

4) We use the xDSL pass `ReconcileUnrealizedCasts`
This pass failed, since `memref` can't be converted to `llvm.ptr`.
The correct way to handle this would be to lower `memref` and not try to convert it, thus going back to step 2, and we get stuck.

> .venv/lib64/python3.14/site-packages/xdsl/transforms/reconcile_unrealized_casts.py:77:
> UserWarning: Unable to remove cast UnrealizedConversionCastOp(
>   %0 = builtin.unrealized_conversion_cast %ssaAlloca : memref<i64> to !llvm.ptr
> )
> because it is not unifiable with its uses

### Solutions to try:
- Implement `convertMemRefToPtr` for `memref.alloca`, but is it non-trivial?
- Try using the passes in a different order?
- Replace `xdsl_ptr` with `ptr` in hopes of better compatibility?
