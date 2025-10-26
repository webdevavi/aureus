import { BASE_API_URL } from "@/config/settings";
import type { ReportFile } from "@/types/report-file";
import { useQuery, type UseQueryOptions } from "@tanstack/react-query";

export const useGetReportFiles = (
  report_id: number,
  options: Omit<UseQueryOptions<ReportFile[]>, "queryKey" | "queryFn"> = {}
) => {
  return useQuery<ReportFile[]>({
    queryKey: ["report-files", report_id.toString()],
    queryFn: async () => {
      const response = await fetch(
        `${BASE_API_URL}/reports/${report_id}/files`,
        {
          method: "GET",
          headers: { "Content-Type": "application/json" },
        }
      );

      return response.json();
    },
    ...options,
  });
};
