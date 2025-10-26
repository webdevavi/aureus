import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Trash2Icon, Loader2Icon } from "lucide-react";
import { toast } from "sonner";
import { useDeleteReport } from "@/api/mutations/use-delete-report";

interface DeleteReportProps {
  report_id: number;
  company_name?: string;
  onDeleted?: () => void;
}

export const DeleteReport: React.FC<DeleteReportProps> = ({
  report_id,
  company_name,
  onDeleted,
}) => {
  const [open, setOpen] = useState(false);
  const { mutateAsync: deleteReport, isPending } = useDeleteReport();

  const handleConfirmDelete = async () => {
    try {
      await deleteReport(report_id);
      toast.success("Report deleted successfully");
      setOpen(false);
      onDeleted?.();
    } catch {
      toast.error("Failed to delete report");
    }
  };

  return (
    <>
      <Button
        variant="destructive"
        size="sm"
        onClick={() => setOpen(true)}
        className="flex items-center gap-1"
      >
        <Trash2Icon className="h-4 w-4" />
        Delete
      </Button>

      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete Report</DialogTitle>
            <DialogDescription>
              Are you sure you want to permanently delete{" "}
              <span className="font-semibold text-foreground">
                {company_name || "this report"}
              </span>
              ? This action cannot be undone.
            </DialogDescription>
          </DialogHeader>

          <DialogFooter className="flex justify-end gap-2 pt-4">
            <Button
              variant="outline"
              onClick={() => setOpen(false)}
              disabled={isPending}
            >
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={handleConfirmDelete}
              disabled={isPending}
              className="flex items-center gap-2"
            >
              {isPending ? (
                <>
                  <Loader2Icon className="h-4 w-4 animate-spin" />
                  Deleting...
                </>
              ) : (
                "Delete"
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
};
