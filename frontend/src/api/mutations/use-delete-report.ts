import { useMutation } from "@tanstack/react-query";
import axios from "axios";
import { queryClient } from "@/api/query-client";
import { BASE_API_URL } from "@/config/settings";

export const useDeleteReport = () => {
  return useMutation({
    mutationFn: async (report_id: number) => {
      const res = await axios.delete(`${BASE_API_URL}/reports/${report_id}`);
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["reports"] });
    },
    onError: (err: any) => {
      console.error("Failed to delete report:", err);
      throw err;
    },
  });
};
