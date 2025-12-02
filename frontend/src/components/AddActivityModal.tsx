import React, { useEffect } from "react";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Typography,
  CircularProgress,
  Box,
  Grid,
} from "@mui/material";
import { useForm, Controller } from "react-hook-form";
import { DateTimePicker } from "@mui/x-date-pickers/DateTimePicker";
import { LocalizationProvider } from "@mui/x-date-pickers/LocalizationProvider";
import { AdapterDateFns } from "@mui/x-date-pickers/AdapterDateFns";

interface AddActivityModalProps {
  open: boolean;
  onClose: () => void;
  onAdd: (data: any) => Promise<void>;
  loading?: boolean;
}

interface ActivityFormData {
  activity_type: string;
  subject: string;
  description?: string;
  outcome?: string;
  activity_date: Date;
  duration_minutes?: number;
}

const activityTypes = ["call", "email", "meeting", "note", "task"];

const outcomes = ["completed", "no_answer", "follow_up_required", "successful", "unsuccessful"];

const AddActivityModal: React.FC<AddActivityModalProps> = ({
  open,
  onClose,
  onAdd,
  loading = false,
}) => {
  const {
    register,
    handleSubmit,
    reset,
    control,
    formState: { errors },
  } = useForm<ActivityFormData>({
    defaultValues: {
      activity_type: "call",
      subject: "",
      description: "",
      outcome: "",
      activity_date: new Date(),
      duration_minutes: 0,
    },
  });

  useEffect(() => {
    if (open) {
      reset();
    }
  }, [open, reset]);

  const onSubmit = async (data: ActivityFormData) => {
    try {
      await onAdd(data);
      reset();
      onClose();
    } catch (err) {
      console.error(err);
    }
  };

  const handleClose = () => {
    if (!loading) {
      reset();
      onClose();
    }
  };

  return (
    <LocalizationProvider dateAdapter={AdapterDateFns}>
      <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
        <DialogTitle>
          <Typography variant="h6" component="div">
            Add Activity
          </Typography>
        </DialogTitle>
        <form onSubmit={handleSubmit(onSubmit)}>
          <DialogContent>
            <Box sx={{ mt: 1 }}>
              <Grid container spacing={3}>
                <Grid size={{ xs: 12 }}>
                  <FormControl fullWidth disabled={loading}>
                    <InputLabel>Activity Type</InputLabel>
                    <Controller
                      name="activity_type"
                      control={control}
                      rules={{ required: "Activity type is required" }}
                      render={({ field }) => (
                        <Select {...field} label="Activity Type" error={!!errors.activity_type}>
                          {activityTypes.map((type) => (
                            <MenuItem key={type} value={type}>
                              {type.charAt(0).toUpperCase() + type.slice(1)}
                            </MenuItem>
                          ))}
                        </Select>
                      )}
                    />
                    {errors.activity_type && (
                      <Typography variant="caption" color="error" sx={{ mt: 0.5, ml: 2 }}>
                        {errors.activity_type.message}
                      </Typography>
                    )}
                  </FormControl>
                </Grid>
                <Grid size={{ xs: 12 }}>
                  <TextField
                    {...register("subject", {
                      required: "Subject is required",
                      minLength: { value: 3, message: "Subject must be at least 3 characters" },
                    })}
                    label="Subject"
                    fullWidth
                    error={!!errors.subject}
                    helperText={errors.subject?.message}
                    disabled={loading}
                  />
                </Grid>
                <Grid size={{ xs: 12 }}>
                  <TextField
                    {...register("description")}
                    label="Description"
                    multiline
                    rows={4}
                    fullWidth
                    disabled={loading}
                  />
                </Grid>
                <Grid size={{ xs: 12 }}>
                  <FormControl fullWidth disabled={loading}>
                    <InputLabel>Outcome</InputLabel>
                    <Controller
                      name="outcome"
                      control={control}
                      render={({ field }) => (
                        <Select {...field} label="Outcome" error={!!errors.outcome}>
                          <MenuItem value="">None</MenuItem>
                          {outcomes.map((outcome) => (
                            <MenuItem key={outcome} value={outcome}>
                              {outcome.replace("_", " ").charAt(0).toUpperCase() + outcome.replace("_", " ").slice(1)}
                            </MenuItem>
                          ))}
                        </Select>
                      )}
                    />
                  </FormControl>
                </Grid>
                <Grid size={{ xs: 12, sm: 6 }}>
                  <Controller
                    name="activity_date"
                    control={control}
                    rules={{ required: "Activity date is required" }}
                    render={({ field }) => (
                      <DateTimePicker
                        label="Activity Date"
                        value={field.value}
                        onChange={field.onChange}
                        disabled={loading}
                        slotProps={{
                          textField: {
                            fullWidth: true,
                            error: !!errors.activity_date,
                            helperText: errors.activity_date?.message,
                          },
                        }}
                      />
                    )}
                  />
                </Grid>
                <Grid size={{ xs: 12, sm: 6 }}>
                  <TextField
                    {...register("duration_minutes", {
                      min: { value: 0, message: "Duration must be positive" },
                    })}
                    label="Duration (minutes)"
                    type="number"
                    fullWidth
                    error={!!errors.duration_minutes}
                    helperText={errors.duration_minutes?.message}
                    disabled={loading}
                    inputProps={{ min: 0 }}
                  />
                </Grid>
              </Grid>
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={handleClose} disabled={loading} color="inherit">
              Cancel
            </Button>
            <Button
              type="submit"
              variant="contained"
              disabled={loading}
              startIcon={loading ? <CircularProgress size={20} /> : null}
            >
              {loading ? "Adding..." : "Add Activity"}
            </Button>
          </DialogActions>
        </form>
      </Dialog>
    </LocalizationProvider>
  );
};

export default AddActivityModal;