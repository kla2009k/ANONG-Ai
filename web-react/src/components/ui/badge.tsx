import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-semibold",
  {
    variants: {
      variant: {
        default: "bg-primary/15 text-primary border border-primary/30",
        accent: "bg-accent/15 text-accent border border-accent/30",
        demo: "bg-amber-400/15 text-amber-300 border border-amber-400/30",
        real: "bg-primary/15 text-primary border border-primary/30",
        muted: "bg-muted text-muted-foreground border border-border",
      },
    },
    defaultVariants: { variant: "default" },
  }
);

export function Badge({
  className,
  variant,
  ...props
}: React.HTMLAttributes<HTMLSpanElement> & VariantProps<typeof badgeVariants>) {
  return <span className={cn(badgeVariants({ variant }), className)} {...props} />;
}
