import { useRetryReportProcessing } from "@/api/mutations/use-retry-report-processing";
import { useGetReportFiles } from "@/api/queries/use-get-report-files";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import type { Report } from "@/types/report";
import {
  AlertCircle,
  Building2,
  Loader2,
  RefreshCcw,
  Upload,
} from "lucide-react";
import React, { useEffect, useState } from "react";
import { toast } from "sonner";
import { Badge } from "../ui/badge";
import { Button } from "../ui/button";
import { Label } from "../ui/label";
import { Separator } from "../ui/separator";
import { Skeleton } from "../ui/skeleton";
import { ReportFileItem } from "./report-file";
import { UploadReportSourceFile } from "./upload-report-source-file";

interface ReportItemModalProps {
  report: Report;
  onClose?: () => void;
}

export const ReportItemModal: React.FC<ReportItemModalProps> = ({
  report,
  onClose,
}) => {
  const [isOpen, setIsOpen] = useState(true);

  useEffect(() => {
    if (!isOpen) onClose?.();
  }, [isOpen, onClose]);

  const { data, isFetching, refetch } = useGetReportFiles(report.id, {
    refetchInterval: 5000,
  });

  const { mutateAsync: retryProcessing, isPending: isRetrying } =
    useRetryReportProcessing();

  const sourceFile = data?.find((file) => file.category === "source");
  const extractFile = data?.find((file) => file.category === "extract");
  const outputFile = data?.find((file) => file.category === "output");

  const hasFailed =
    [extractFile, outputFile].some((f) => f?.status === "error") ?? false;

  const handleRetry = async () => {
    try {
      const res = await retryProcessing(report.id);
      toast.success(res.message || "Retry initiated successfully");
      await refetch();
    } catch (err) {
      toast.error((err as Error).message || "Retry failed");
    }
  };

  const renderFiles = () => {
    if (isFetching && !data) {
      return (
        <div className="space-y-4">
          <div>
            <div className="flex items-center justify-between mb-3">
              <Label className="text-sm font-semibold">
                Processing Pipeline
              </Label>
              <Badge variant="secondary" className="text-xs">
                Loading
              </Badge>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <Skeleton className="h-28 rounded-lg" />
              <Skeleton className="h-28 rounded-lg" />
              <Skeleton className="h-28 rounded-lg" />
            </div>
          </div>
        </div>
      );
    }

    if (sourceFile) {
      const processingCount = [sourceFile, extractFile, outputFile].filter(
        (f) => f?.status === "processing"
      ).length;
      const completedCount = [sourceFile, extractFile, outputFile].filter(
        (f) => f?.status === "done"
      ).length;
      const totalFiles = [sourceFile, extractFile, outputFile].filter(
        Boolean
      ).length;

      return (
        <div className="space-y-4">
          <div>
            <div className="flex items-center justify-between mb-3">
              <Label className="text-sm font-semibold">
                Processing Pipeline
              </Label>
              <Badge
                variant={
                  hasFailed
                    ? "destructive"
                    : processingCount > 0
                    ? "secondary"
                    : "default"
                }
                className="text-xs"
              >
                {hasFailed ? (
                  <>
                    <AlertCircle className="h-3 w-3 mr-1" />
                    Error
                  </>
                ) : processingCount > 0 ? (
                  <>
                    <Loader2 className="h-3 w-3 mr-1 animate-spin" />
                    Processing
                  </>
                ) : (
                  `${completedCount}/${totalFiles} Complete`
                )}
              </Badge>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <ReportFileItem file={sourceFile} />

              {extractFile && <ReportFileItem file={extractFile} />}
              {outputFile && <ReportFileItem file={outputFile} />}
            </div>
          </div>
        </div>
      );
    }

    return (
      <div className="space-y-4">
        <div className="rounded-lg border border-dashed p-6 text-center space-y-3">
          <div className="mx-auto w-12 h-12 rounded-full bg-secondary flex items-center justify-center">
            <Upload className="h-6 w-6" />
          </div>
          <div>
            <Label className="text-base font-semibold block mb-1">
              Upload Source File
            </Label>
            <p className="text-xs text-muted-foreground mb-4">
              Upload a document to begin processing
            </p>
          </div>
          <UploadReportSourceFile report_id={report.id} />
        </div>
      </div>
    );
  };

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogContent className="sm:max-w-3xl">
        <DialogHeader className="space-y-3">
          <div className="flex items-start justify-between gap-4">
            <div className="space-y-1 flex-1">
              <DialogTitle className="text-xl font-bold flex items-center gap-2">
                <Building2 className="h-5 w-5 text-muted-foreground" />
                {report.company_name}
              </DialogTitle>
              <DialogDescription className="text-sm">
                View and manage report processing status
              </DialogDescription>
            </div>
            {hasFailed && (
              <Button
                variant="destructive"
                size="sm"
                onClick={handleRetry}
                disabled={isRetrying}
                className="flex items-center gap-1.5 shadow-sm hover:shadow transition-all shrink-0"
              >
                {isRetrying ? (
                  <Loader2 className="h-3.5 w-3.5 animate-spin" />
                ) : (
                  <RefreshCcw className="h-3.5 w-3.5" />
                )}
                {isRetrying ? "Retrying..." : "Retry Processing"}
              </Button>
            )}
          </div>
          <Separator />
        </DialogHeader>

        <div className="mt-2">{renderFiles()}</div>
      </DialogContent>
    </Dialog>
  );
};
