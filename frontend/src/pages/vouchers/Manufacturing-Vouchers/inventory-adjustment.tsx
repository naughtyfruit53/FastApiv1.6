// frontend/src/pages/vouchers/Manufacturing-Vouchers/inventory-adjustment.tsx
import React, { useState, useEffect } from "react";
import { Typography, Container, Box, Button, Grid, CircularProgress } from "@mui/material";
import { useForm } from "react-hook-form";
import { yupResolver } from "@hookform/resolvers/yup";
import * as yup from "yup";
import { ProtectedPage } from "../../../components/ProtectedPage";
import { useAuth } from "../../../context/AuthContext";
import api from "../../../services/api/client"; // Assuming this is your API client

// Define form schema
const schema = yup.object().shape({
  type: yup.string().oneOf(["increase", "decrease", "conversion", "wip", "write-off"]).required("Type is required"),
  itemId: yup.number().required("Item is required"),
  batchNumber: yup.string(),
  oldQuantity: yup.number().required("Old Quantity is required"),
  newQuantity: yup.number().required("New Quantity is required"),
  reason: yup.string().oneOf(["audit", "damage", "wastage", "theft", "error", "remeasure"]).required("Reason is required"),
  documents: yup.array().of(yup.mixed()),
});

interface InventoryAdjustmentFormData {
  type: string;
  itemId: number;
  batchNumber?: string;
  oldQuantity: number;
  newQuantity: number;
  reason: string;
  documents?: File[];
}

const InventoryAdjustment: React.FC = () => {
  const { user } = useAuth();
  const [items, setItems] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [submitLoading, setSubmitLoading] = useState(false);

  const { control, handleSubmit, formState: { errors }, reset } = useForm<InventoryAdjustmentFormData>({
    resolver: yupResolver(schema),
  });

  useEffect(() => {
    const fetchItems = async () => {
      try {
        const response = await api.get("/products"); 
        setItems(response.data);
      } catch (error) {
        console.error("Error fetching items:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchItems();
  }, []);

  const onSubmit = async (data: InventoryAdjustmentFormData) => {
    setSubmitLoading(true);
    try {
      const formData = new FormData();
      if (data.documents) {
        data.documents.forEach((file) => formData.append("documents", file));
      }
      await api.post("/manufacturing/inventory-adjustment", data);
      reset();
      alert("Inventory adjustment recorded successfully!");
    } catch (error) {
      console.error("Error submitting inventory adjustment:", error);
      alert("Failed to record inventory adjustment.");
    } finally {
      setSubmitLoading(false);
    }
  };

  if (loading) {
    return <CircularProgress />;
  }

  return (
    <ProtectedPage moduleKey="manufacturing" action="write">
      <Container maxWidth="lg">
        <Box sx={{ mt: 3 }}>
          <Typography variant="h4" gutterBottom>
            Inventory Adjustment
          </Typography>
          <Typography variant="body1" color="text.secondary" paragraph>
            Adjust inventory for production variances, waste, or discrepancies.
          </Typography>

          <form onSubmit={handleSubmit(onSubmit)}>
            <Grid container spacing={2}>
              {/* Add all fields from schema */}
              <Grid item xs={12}>
                <Button type="submit" variant="contained" disabled={submitLoading}>
                  {submitLoading ? <CircularProgress size={24} /> : "Submit Adjustment"}
                </Button>
              </Grid>
            </Grid>
          </form>
        </Box>
      </Container>
    </ProtectedPage>
  );
};

export default InventoryAdjustment;