import { BASE_API_URL } from "@/config/settings";
import { useQuery } from "@tanstack/react-query";

export const useGetPresignedUrlForFileDownload = (
  report_id: number,
  file_id: number
) => {
  return useQuery<{ download_url: string }>({
    queryKey: ["download-report-file", report_id.toString(), file_id],
    queryFn: async () => {
      const response = await fetch(
        `${BASE_API_URL}/reports/${report_id}/files/${file_id}`,
        { method: "GET", headers: { "Content-Type": "application/json" } }
      );

      return response.json();
    },
  });
};
