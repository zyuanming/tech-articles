; Original small illustrative LLVM IR, based on LLVM 18.1.8 LangRef syntax.
; CC BY 4.0. Shown as source text; this environment did not execute LLVM.
define i32 @bonus(i1 %flag) {
entry:
  br i1 %flag, label %left, label %right
left:
  br label %join
right:
  br label %join
join:
  %x = phi i32 [ 3, %left ], [ 1, %right ]
  %y = add i32 %x, 2
  ret i32 %y
}
