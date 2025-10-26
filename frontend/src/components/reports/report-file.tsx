import type { ReportFile } from "@/types/report-file";
import { DownloadIcon, AlertCircle, CheckCircle2, Loader2 } from "lucide-react";
import React from "react";
import { Button } from "../ui/button";
import {
  Item,
  ItemActions,
  ItemContent,
  ItemTitle,
  ItemDescription,
} from "../ui/item";
import { useGetPresignedUrlForFileDownload } from "@/api/queries/use-get-presigned-url-for-file-download";
import { cn } from "@/lib/utils";
import { Skeleton } from "../ui/skeleton";

export interface ReportFileItemProps {
  file: ReportFile;
}

export const ReportFileItem: React.FC<ReportFileItemProps> = ({ file }) => {
  const { data, isFetching } = useGetPresignedUrlForFileDownload(
    file.report_id,
    file.id
  );

  const renderStatus = () => {
    switch (file.status) {
      case "pending":
        return (
          <div className="flex items-center gap-1 text-muted-foreground">
            <Loader2 className="size-3 animate-spin" />
            <span className="text-xs">Pending</span>
          </div>
        );
      case "processing":
        return (
          <div className="flex items-center gap-1 text-muted-foreground">
            <Loader2 className="size-3 animate-spin" />
            <span className="text-xs">Processing</span>
          </div>
        );
      case "done":
        return (
          <div className="flex items-center gap-1 text-green-600 dark:text-green-400">
            <CheckCircle2 className="size-3" />
            <span className="text-xs">Done</span>
          </div>
        );
      case "error":
        return (
          <div className="flex items-center gap-1 text-destructive">
            <AlertCircle className="size-3" />
            <span className="text-xs">Error</span>
          </div>
        );
      default:
        return (
          <span className="text-xs text-muted-foreground capitalize">
            {file.status}
          </span>
        );
    }
  };

  const isDownloadable = file.status === "done" && !!data?.download_url;

  return (
    <Item
      variant="outline"
      className={cn(
        "flex flex-col items-stretch transition-colors duration-150",
        file.status === "error" && "border-destructive/50 bg-destructive/5",
        file.status === "done" && "border-green-500/30 bg-green-500/5"
      )}
    >
      <ItemContent>
        <div className="w-full flex items-center justify-between">
          <ItemTitle className="uppercase tracking-wide text-sm">
            {file.category}
          </ItemTitle>
          {/* 🧩 File type badge */}
          <span className="text-[11px] font-medium uppercase text-muted-foreground">
            {file.type}
          </span>
        </div>

        <ItemDescription className="flex flex-col text-xs mt-1">
          {renderStatus()}
          {file.error && (
            <span className="mt-0.5 text-destructive text-[11px] leading-snug">
              {file.error}
            </span>
          )}
        </ItemDescription>
      </ItemContent>

      <ItemActions className="flex items-center gap-1">
        {file.status === "done" && (
          <>
            {isFetching ? (
              <Skeleton className="h-6 w-20 rounded-md" />
            ) : (
              <Button
                size="sm"
                variant="outline"
                disabled={!isDownloadable}
                onClick={() =>
                  data?.download_url && window.open(data.download_url, "_blank")
                }
                className={cn(
                  "flex items-center gap-1",
                  "hover:bg-accent focus-visible:ring-1 focus-visible:ring-ring"
                )}
              >
                <DownloadIcon className="size-4" />
                Download
              </Button>
            )}
          </>
        )}

        {(file.status === "pending" || file.status === "processing") && (
          <Button size="sm" variant="ghost" disabled className="opacity-60">
            <Loader2 className="size-4 animate-spin" />
            Generating
          </Button>
        )}
      </ItemActions>
    </Item>
  );
};
