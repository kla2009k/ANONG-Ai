import type { ReactNode, CSSProperties } from "react";
import { cn } from "@/lib/utils";

/** Layout wrapper kept visible by default; product content must never depend on animation. */
export function Reveal({
  children,
  className,
  as: Tag = "div",
  style,
}: {
  children: ReactNode;
  className?: string;
  dir?: "l" | "r";
  delay?: number;
  as?: any;
  style?: CSSProperties;
}) {
  return (
    <Tag
      style={style}
      className={cn(className)}
    >
      {children}
    </Tag>
  );
}
