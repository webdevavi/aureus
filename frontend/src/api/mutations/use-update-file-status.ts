import { BASE_API_URL } from "@/config/settings";
import type { FileStatus } from "@/types/report-file";
import { useMutation } from "@tanstack/react-query";

export const useUpdateFileStatus = (report_id: number) => {
  return useMutation<
    { id: number; status: FileStatus; error?: string | null },
    Error,
    { file_id: number; status: FileStatus; error_message?: string }
  >({
    mutationKey: ["update-file-status", report_id.toString()],
    mutationFn: async ({ file_id, status, error_message }) => {
      const res = await fetch(
        `${BASE_API_URL}/reports/${report_id}/files/${file_id}/status`,
        {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            status,
            ...(error_message ? { error_message } : {}),
          }),
        }
      );

      if (!res.ok) {
        const text = await res.text();
        throw new Error(
          `Failed to update file status: ${res.status} - ${text}`
        );
      }

      return res.json();
    },
  });
};
