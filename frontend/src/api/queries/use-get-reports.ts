import { BASE_API_URL } from "@/config/settings";
import type { Report } from "@/types/report";
import { useQuery } from "@tanstack/react-query";

export const useGetReports = () => {
  return useQuery<Report[]>({
    queryKey: ["reports"],
    queryFn: async () => {
      const response = await fetch(`${BASE_API_URL}/reports`, {
        method: "GET",
        headers: { "Content-Type": "application/json" },
      });

      return response.json();
    },
  });
};
