import { useRetryReportProcessing } from "@/api/mutations/use-retry-report-processing";
import { useGetReportFiles } from "@/api/queries/use-get-report-files";
import type { Report } from "@/types/report";
import { ClipboardIcon, Loader2, RefreshCcw } from "lucide-react";
import React from "react";
import { toast } from "sonner";
import { Button } from "../ui/button";
import {
  Item,
  ItemActions,
  ItemContent,
  ItemDescription,
  ItemMedia,
  ItemTitle,
} from "../ui/item";
import { Skeleton } from "../ui/skeleton";
import { DeleteReport } from "./delete-report";
import { ReportFileItem } from "./report-file";

export interface ReportItemProps {
  report: Report;
  onSelect?: (report: Report) => void;
}

export const ReportItem: React.FC<ReportItemProps> = ({ report, onSelect }) => {
  const { data, isFetching, refetch } = useGetReportFiles(report.id);
  const { mutateAsync: retryProcessing, isPending: isRetrying } =
    useRetryReportProcessing();

  const sourceFile = data?.find((file) => file.category === "source");
  const extractFile = data?.find((file) => file.category === "extract");
  const outputFile = data?.find((file) => file.category === "output");

  const hasFailed =
    [sourceFile, extractFile, outputFile].some(
      (f) => f && f.status === "error"
    ) ?? false;

  const handleRetry = async () => {
    try {
      const res = await retryProcessing(report.id);
      toast.success(res.message || "Retry initiated successfully");
      await refetch();
      onSelect?.(report);
    } catch (err) {
      toast.error((err as Error).message || "Retry failed");
    }
  };

  if (!sourceFile) {
    return (
      <Item
        variant="outline"
        role="listitem"
        className="hover:bg-accent/50 transition-colors"
      >
        <ItemMedia variant="icon">
          <ClipboardIcon className="size-4" />
        </ItemMedia>
        <ItemContent>
          <ItemTitle className="uppercase font-semibold">
            {report.company_name}
          </ItemTitle>
          {onSelect && (
            <ItemActions>
              <Button size="sm" onClick={() => onSelect(report)}>
                Process Now
              </Button>
              <DeleteReport report_id={report.id} />
            </ItemActions>
          )}
        </ItemContent>
      </Item>
    );
  }

  return (
    <Item
      variant="outline"
      role="listitem"
      className="hover:bg-accent/50 transition-colors cursor-pointer"
      onClick={() => onSelect?.(report)}
    >
      <ItemMedia variant="icon">
        <ClipboardIcon className="size-4" />
      </ItemMedia>

      <ItemContent className="flex flex-col gap-2">
        <ItemTitle className="uppercase flex items-center justify-between font-semibold">
          <span>{report.company_name}</span>

          {hasFailed && (
            <Button
              variant="destructive"
              size="sm"
              onClick={handleRetry}
              disabled={isRetrying}
              className="flex items-center gap-1"
            >
              {isRetrying ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <RefreshCcw className="h-4 w-4" />
              )}
              {isRetrying ? "Retrying..." : "Retry"}
            </Button>
          )}
        </ItemTitle>

        <ItemDescription className="grid grid-cols-3 gap-2 mt-1">
          {isFetching && !data ? (
            <>
              <Skeleton className="h-20 rounded-md" />
              <Skeleton className="h-20 rounded-md" />
              <Skeleton className="h-20 rounded-md" />
            </>
          ) : (
            <>
              {sourceFile && <ReportFileItem file={sourceFile} />}
              {extractFile && <ReportFileItem file={extractFile} />}
              {outputFile && <ReportFileItem file={outputFile} />}
            </>
          )}
        </ItemDescription>

        <ItemActions className="w-min" onClick={(e) => e.stopPropagation()}>
          <DeleteReport report_id={report.id} />
        </ItemActions>
      </ItemContent>
    </Item>
  );
};
