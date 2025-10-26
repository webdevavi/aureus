import { BASE_API_URL } from "@/config/settings";
import { useMutation } from "@tanstack/react-query";

interface RetryResponse {
  report_id: number;
  retry_stage: "extractor" | "renderer";
  queued: boolean;
  message: string;
}

export const useRetryReportProcessing = () => {
  return useMutation<RetryResponse, Error, number>({
    mutationKey: ["retry-report-processing"],
    mutationFn: async (report_id: number) => {
      const res = await fetch(`${BASE_API_URL}/reports/${report_id}/retry`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
      });

      if (!res.ok) {
        const text = await res.text();
        throw new Error(`Retry request failed: ${res.status} - ${text}`);
      }

      return res.json();
    },
  });
};
