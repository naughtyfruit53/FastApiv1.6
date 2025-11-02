// frontend/src/services/resetService.ts

import axios from "axios";
import { getApiUrl } from "../utils/config";

const API_BASE_URL = getApiUrl();

export const requestResetOTP = async (
  scope: string,
  organization_id?: number,
): Promise<any> => {
  try {
    const token = localStorage.getItem("token");
    const response = await axios.post(
      `${API_BASE_URL}/organizations/reset-data/request-otp`,
      {
        scope: scope.toUpperCase(),
        organization_id,
      },
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      },
    );
    return response.data;
  } catch (error: any) {
    throw new Error(
      error.response?.data?.detail || "Failed to request reset OTP",
    );
  }
};

export const confirmReset = async (otp: string): Promise<any> => {
  try {
    const token = localStorage.getItem("token");
    const response = await axios.post(
      `${API_BASE_URL}/organizations/reset-data/verify-otp`,
      { otp },
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      },
    );
    return response.data;
  } catch (error: any) {
    throw new Error(error.response?.data?.detail || "Failed to confirm reset");
  }
};
