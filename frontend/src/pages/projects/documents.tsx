"use client";
import React, { useState } from "react";
import {
  Box,
  Container,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  IconButton,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Card,
  CardContent,
  Stack,
  Menu,
  LinearProgress,
  Avatar,
  Divider,
} from "@mui/material";
import {
  Add,
  Edit,
  Delete,
  Search,
  MoreVert,
  Download,
  Visibility,
  InsertDriveFile,
  Share,
  History,
  FilterList,
  CloudUpload,
  Assessment,
} from "@mui/icons-material";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "react-toastify";

interface ProjectDocument {
  id: number;
  project_id: number;
  project_name?: string;
  name: string;
  description?: string;
  file_path: string;
  file_type: string;
  file_size: number;
  version: string;
  category: "specification" | "design" | "contract" | "report" | "other";
  status: "draft" | "approved" | "archived";
  is_active: boolean;
  uploaded_by: number;
  uploaded_by_name?: string;
  created_at: string;
  updated_at: string;
  tags?: string[];
}

interface DocumentVersion {
  id: number;
  document_id: number;
  version: string;
  file_path: string;
  comment?: string;
  uploaded_by: number;
  uploaded_by_name?: string;
  created_at: string;
}

// Mock API functions - replace with actual API calls
const documentsApi = {
  getDocuments: async (): Promise<ProjectDocument[]> => {
    // Mock data for demonstration
    return [
      {
        id: 1,
        project_id: 1,
        project_name: "Website Redesign",
        name: "Technical Specification",
        description: "Complete technical requirements document",
        file_path: "/documents/tech-spec-v2.pdf",
        file_type: "pdf",
        file_size: 2048000,
        version: "2.1",
        category: "specification",
        status: "approved",
        is_active: true,
        uploaded_by: 1,
        uploaded_by_name: "John Doe",
        created_at: "2024-01-15T10:00:00Z",
        updated_at: "2024-01-20T14:30:00Z",
        tags: ["specification", "requirements", "technical"]
      },
      {
        id: 2,
        project_id: 1,
        project_name: "Website Redesign",
        name: "UI Mockups",
        description: "User interface design mockups",
        file_path: "/documents/ui-mockups.figma",
        file_type: "figma",
        file_size: 1024000,
        version: "1.0",
        category: "design",
        status: "draft",
        is_active: true,
        uploaded_by: 2,
        uploaded_by_name: "Jane Smith",
        created_at: "2024-01-18T09:15:00Z",
        updated_at: "2024-01-18T09:15:00Z",
        tags: ["design", "ui", "mockups"]
      }
    ];
  },

  createDocument: async (data: Partial<ProjectDocument>): Promise<ProjectDocument> => {
    console.log("Creating document:", data);
    return { ...data, id: Date.now() } as ProjectDocument;
  },

  updateDocument: async (id: number, data: Partial<ProjectDocument>): Promise<ProjectDocument> => {
    console.log("Updating document:", id, data);
    return { ...data, id } as ProjectDocument;
  },

  deleteDocument: async (id: number): Promise<void> => {
    console.log("Deleting document:", id);
  },

  getVersionHistory: async (documentId: number): Promise<DocumentVersion[]> => {
    return [
      {
        id: 1,
        document_id: documentId,
        version: "2.1",
        file_path: "/documents/tech-spec-v2.1.pdf",
        comment: "Updated API specifications",
        uploaded_by: 1,
        uploaded_by_name: "John Doe",
        created_at: "2024-01-20T14:30:00Z"
      },
      {
        id: 2,
        document_id: documentId,
        version: "2.0",
        file_path: "/documents/tech-spec-v2.0.pdf",
        comment: "Major revision with new requirements",
        uploaded_by: 1,
        uploaded_by_name: "John Doe",
        created_at: "2024-01-18T10:00:00Z"
      }
    ];
  }
};

const ProjectDocumentsPage: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState("");
  const [filterCategory, setFilterCategory] = useState<string>("all");
  const [filterStatus, setFilterStatus] = useState<string>("all");
  const [addDialog, setAddDialog] = useState(false);
  const [editDialog, setEditDialog] = useState(false);
  const [versionDialog, setVersionDialog] = useState(false);
  const [selectedDocument, setSelectedDocument] = useState<ProjectDocument | null>(null);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [menuDocument, setMenuDocument] = useState<ProjectDocument | null>(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  
  const [formData, setFormData] = useState({
    project_id: "",
    name: "",
    description: "",
    category: "specification" as ProjectDocument["category"],
    status: "draft" as ProjectDocument["status"],
    tags: "",
    file: null as File | null,
  });

  const queryClient = useQueryClient();

  // Fetch documents
  const { data: documents = [], isLoading, error } = useQuery({
    queryKey: ['projectDocuments'],
    queryFn: documentsApi.getDocuments,
  });

  // Fetch version history
  const { data: versions = [] } = useQuery({
    queryKey: ['documentVersions', selectedDocument?.id],
    queryFn: () => selectedDocument ? documentsApi.getVersionHistory(selectedDocument.id) : Promise.resolve([]),
    enabled: !!selectedDocument && versionDialog,
  });

  // Create document mutation
  const createMutation = useMutation({
    mutationFn: documentsApi.createDocument,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projectDocuments'] });
      setAddDialog(false);
      resetForm();
      toast.success("Document uploaded successfully");
    },
    onError: (error) => {
      toast.error("Failed to upload document");
      console.error("Error creating document:", error);
    },
  });

  // Update document mutation
  const updateMutation = useMutation({
    mutationFn: ({ id, ...data }: { id: number } & Partial<ProjectDocument>) =>
      documentsApi.updateDocument(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projectDocuments'] });
      setEditDialog(false);
      resetForm();
      toast.success("Document updated successfully");
    },
    onError: (error) => {
      toast.error("Failed to update document");
      console.error("Error updating document:", error);
    },
  });

  // Delete document mutation
  const deleteMutation = useMutation({
    mutationFn: documentsApi.deleteDocument,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projectDocuments'] });
      toast.success("Document deleted successfully");
    },
    onError: (error) => {
      toast.error("Failed to delete document");
      console.error("Error deleting document:", error);
    },
  });

  const resetForm = () => {
    setFormData({
      project_id: "",
      name: "",
      description: "",
      category: "specification",
      status: "draft",
      tags: "",
      file: null,
    });
    setSelectedDocument(null);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (editDialog && selectedDocument) {
      updateMutation.mutate({
        id: selectedDocument.id,
        ...formData,
        tags: formData.tags.split(',').map(tag => tag.trim()).filter(Boolean),
      });
    } else {
      createMutation.mutate({
        ...formData,
        tags: formData.tags.split(',').map(tag => tag.trim()).filter(Boolean),
      });
    }
  };

  const handleEdit = (document: ProjectDocument) => {
    setSelectedDocument(document);
    setFormData({
      project_id: document.project_id.toString(),
      name: document.name,
      description: document.description || "",
      category: document.category,
      status: document.status,
      tags: document.tags?.join(', ') || "",
      file: null,
    });
    setEditDialog(true);
    setAnchorEl(null);
  };

  const handleDelete = (document: ProjectDocument) => {
    if (window.confirm(`Are you sure you want to delete "${document.name}"?`)) {
      deleteMutation.mutate(document.id);
    }
    setAnchorEl(null);
  };

  const handleViewVersions = (document: ProjectDocument) => {
    setSelectedDocument(document);
    setVersionDialog(true);
    setAnchorEl(null);
  };

  const handleMenuClick = (event: React.MouseEvent<HTMLElement>, document: ProjectDocument) => {
    setAnchorEl(event.currentTarget);
    setMenuDocument(document);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    setMenuDocument(null);
  };

  const handleFileUpload = (file: File) => {
    setFormData(prev => ({ ...prev, file }));
    // Simulate upload progress
    setUploadProgress(0);
    const interval = setInterval(() => {
      setUploadProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval);
          return 100;
        }
        return prev + 10;
      });
    }, 200);
  };

  const getFileIcon = (fileType: string) => {
    switch (fileType.toLowerCase()) {
      case 'pdf':
        return <Assessment color="error" />;
      case 'doc':
      case 'docx':
        return <InsertDriveFile color="primary" />;
      case 'figma':
        return <InsertDriveFile color="secondary" />;
      default:
        return <InsertDriveFile />;
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getStatusColor = (status: ProjectDocument["status"]) => {
    switch (status) {
      case "approved": return "success";
      case "draft": return "warning";
      case "archived": return "default";
      default: return "default";
    }
  };

  const getCategoryColor = (category: ProjectDocument["category"]) => {
    switch (category) {
      case "specification": return "primary";
      case "design": return "secondary";
      case "contract": return "info";
      case "report": return "success";
      default: return "default";
    }
  };

  // Filter documents
  const filteredDocuments = documents.filter(doc => {
    const matchesSearch = doc.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         doc.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         doc.project_name?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = filterCategory === "all" || doc.category === filterCategory;
    const matchesStatus = filterStatus === "all" || doc.status === filterStatus;
    
    return matchesSearch && matchesCategory && matchesStatus;
  });

  if (isLoading) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Alert severity="error">Failed to load documents</Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1" fontWeight="bold">
          Project Documents
        </Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => setAddDialog(true)}
        >
          Upload Document
        </Button>
      </Box>

      {/* Statistics Cards */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Documents
              </Typography>
              <Typography variant="h5" component="div">
                {documents.length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Approved
              </Typography>
              <Typography variant="h5" component="div" color="success.main">
                {documents.filter(d => d.status === 'approved').length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Draft
              </Typography>
              <Typography variant="h5" component="div" color="warning.main">
                {documents.filter(d => d.status === 'draft').length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Categories
              </Typography>
              <Typography variant="h5" component="div">
                {new Set(documents.map(d => d.category)).size}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Search and Filters */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              placeholder="Search documents..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              InputProps={{
                startAdornment: <Search color="action" sx={{ mr: 1 }} />,
              }}
            />
          </Grid>
          <Grid item xs={12} md={3}>
            <FormControl fullWidth>
              <InputLabel>Category</InputLabel>
              <Select
                value={filterCategory}
                label="Category"
                onChange={(e) => setFilterCategory(e.target.value)}
              >
                <MenuItem value="all">All Categories</MenuItem>
                <MenuItem value="specification">Specification</MenuItem>
                <MenuItem value="design">Design</MenuItem>
                <MenuItem value="contract">Contract</MenuItem>
                <MenuItem value="report">Report</MenuItem>
                <MenuItem value="other">Other</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={3}>
            <FormControl fullWidth>
              <InputLabel>Status</InputLabel>
              <Select
                value={filterStatus}
                label="Status"
                onChange={(e) => setFilterStatus(e.target.value)}
              >
                <MenuItem value="all">All Status</MenuItem>
                <MenuItem value="draft">Draft</MenuItem>
                <MenuItem value="approved">Approved</MenuItem>
                <MenuItem value="archived">Archived</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={2}>
            <Button
              fullWidth
              variant="outlined"
              startIcon={<FilterList />}
              onClick={() => {
                setFilterCategory("all");
                setFilterStatus("all");
                setSearchTerm("");
              }}
            >
              Clear
            </Button>
          </Grid>
        </Grid>
      </Paper>

      {/* Documents Table */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Document</TableCell>
              <TableCell>Project</TableCell>
              <TableCell>Category</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Version</TableCell>
              <TableCell>Size</TableCell>
              <TableCell>Updated</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filteredDocuments.map((document) => (
              <TableRow key={document.id} hover>
                <TableCell>
                  <Box display="flex" alignItems="center">
                    {getFileIcon(document.file_type)}
                    <Box ml={2}>
                      <Typography variant="subtitle2" fontWeight="medium">
                        {document.name}
                      </Typography>
                      <Typography variant="body2" color="textSecondary">
                        {document.description}
                      </Typography>
                      {document.tags && (
                        <Box mt={1}>
                          {document.tags.slice(0, 2).map((tag, index) => (
                            <Chip
                              key={index}
                              label={tag}
                              size="small"
                              sx={{ mr: 0.5 }}
                            />
                          ))}
                          {document.tags.length > 2 && (
                            <Chip
                              label={`+${document.tags.length - 2} more`}
                              size="small"
                              variant="outlined"
                            />
                          )}
                        </Box>
                      )}
                    </Box>
                  </Box>
                </TableCell>
                <TableCell>{document.project_name}</TableCell>
                <TableCell>
                  <Chip
                    label={document.category}
                    color={getCategoryColor(document.category)}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  <Chip
                    label={document.status}
                    color={getStatusColor(document.status)}
                    size="small"
                  />
                </TableCell>
                <TableCell>v{document.version}</TableCell>
                <TableCell>{formatFileSize(document.file_size)}</TableCell>
                <TableCell>
                  <Typography variant="body2">
                    {new Date(document.updated_at).toLocaleDateString()}
                  </Typography>
                  <Typography variant="caption" color="textSecondary">
                    by {document.uploaded_by_name}
                  </Typography>
                </TableCell>
                <TableCell>
                  <IconButton
                    onClick={(e) => handleMenuClick(e, document)}
                    size="small"
                  >
                    <MoreVert />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {filteredDocuments.length === 0 && (
        <Box textAlign="center" py={4}>
          <Typography variant="h6" color="textSecondary">
            No documents found
          </Typography>
          <Typography variant="body2" color="textSecondary" mt={1}>
            Upload your first document to get started
          </Typography>
        </Box>
      )}

      {/* Action Menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={() => menuDocument && handleEdit(menuDocument)}>
          <Edit sx={{ mr: 1 }} fontSize="small" />
          Edit
        </MenuItem>
        <MenuItem onClick={() => menuDocument && handleViewVersions(menuDocument)}>
          <History sx={{ mr: 1 }} fontSize="small" />
          Version History
        </MenuItem>
        <MenuItem>
          <Download sx={{ mr: 1 }} fontSize="small" />
          Download
        </MenuItem>
        <MenuItem>
          <Share sx={{ mr: 1 }} fontSize="small" />
          Share
        </MenuItem>
        <Divider />
        <MenuItem 
          onClick={() => menuDocument && handleDelete(menuDocument)}
          sx={{ color: 'error.main' }}
        >
          <Delete sx={{ mr: 1 }} fontSize="small" />
          Delete
        </MenuItem>
      </Menu>

      {/* Add/Edit Document Dialog */}
      <Dialog 
        open={addDialog || editDialog} 
        onClose={() => {
          setAddDialog(false);
          setEditDialog(false);
          resetForm();
        }}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          {editDialog ? "Edit Document" : "Upload Document"}
        </DialogTitle>
        <form onSubmit={handleSubmit}>
          <DialogContent>
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Document Name"
                  value={formData.name}
                  onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                  required
                  margin="normal"
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Project ID"
                  value={formData.project_id}
                  onChange={(e) => setFormData(prev => ({ ...prev, project_id: e.target.value }))}
                  required
                  margin="normal"
                  type="number"
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Description"
                  value={formData.description}
                  onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                  multiline
                  rows={3}
                  margin="normal"
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <FormControl fullWidth margin="normal">
                  <InputLabel>Category</InputLabel>
                  <Select
                    value={formData.category}
                    label="Category"
                    onChange={(e) => setFormData(prev => ({ ...prev, category: e.target.value as ProjectDocument["category"] }))}
                  >
                    <MenuItem value="specification">Specification</MenuItem>
                    <MenuItem value="design">Design</MenuItem>
                    <MenuItem value="contract">Contract</MenuItem>
                    <MenuItem value="report">Report</MenuItem>
                    <MenuItem value="other">Other</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} md={6}>
                <FormControl fullWidth margin="normal">
                  <InputLabel>Status</InputLabel>
                  <Select
                    value={formData.status}
                    label="Status"
                    onChange={(e) => setFormData(prev => ({ ...prev, status: e.target.value as ProjectDocument["status"] }))}
                  >
                    <MenuItem value="draft">Draft</MenuItem>
                    <MenuItem value="approved">Approved</MenuItem>
                    <MenuItem value="archived">Archived</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Tags (comma separated)"
                  value={formData.tags}
                  onChange={(e) => setFormData(prev => ({ ...prev, tags: e.target.value }))}
                  margin="normal"
                  placeholder="technical, specification, requirements"
                />
              </Grid>
              {!editDialog && (
                <Grid item xs={12}>
                  <Box
                    sx={{
                      border: '2px dashed',
                      borderColor: 'grey.300',
                      borderRadius: 1,
                      p: 3,
                      textAlign: 'center',
                      cursor: 'pointer',
                      '&:hover': { borderColor: 'primary.main' }
                    }}
                    onClick={() => document.getElementById('file-upload')?.click()}
                  >
                    <input
                      id="file-upload"
                      type="file"
                      hidden
                      onChange={(e) => {
                        const file = e.target.files?.[0];
                        if (file) handleFileUpload(file);
                      }}
                    />
                    <CloudUpload sx={{ fontSize: 48, color: 'grey.400', mb: 2 }} />
                    <Typography variant="h6" gutterBottom>
                      {formData.file ? formData.file.name : "Choose file to upload"}
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      Click here or drag and drop your file
                    </Typography>
                    {uploadProgress > 0 && uploadProgress < 100 && (
                      <LinearProgress variant="determinate" value={uploadProgress} sx={{ mt: 2 }} />
                    )}
                  </Box>
                </Grid>
              )}
            </Grid>
          </DialogContent>
          <DialogActions>
            <Button 
              onClick={() => {
                setAddDialog(false);
                setEditDialog(false);
                resetForm();
              }}
            >
              Cancel
            </Button>
            <Button 
              type="submit" 
              variant="contained"
              disabled={createMutation.isPending || updateMutation.isPending}
            >
              {editDialog ? "Update" : "Upload"}
            </Button>
          </DialogActions>
        </form>
      </Dialog>

      {/* Version History Dialog */}
      <Dialog
        open={versionDialog}
        onClose={() => setVersionDialog(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          Version History - {selectedDocument?.name}
        </DialogTitle>
        <DialogContent>
          <Stack spacing={2}>
            {versions.map((version) => (
              <Card key={version.id} variant="outlined">
                <CardContent>
                  <Box display="flex" justifyContent="space-between" alignItems="center">
                    <Box>
                      <Typography variant="h6">
                        Version {version.version}
                      </Typography>
                      <Typography variant="body2" color="textSecondary" gutterBottom>
                        {version.comment}
                      </Typography>
                      <Box display="flex" alignItems="center" mt={1}>
                        <Avatar sx={{ width: 24, height: 24, mr: 1 }}>
                          {version.uploaded_by_name?.charAt(0)}
                        </Avatar>
                        <Typography variant="caption">
                          {version.uploaded_by_name} • {new Date(version.created_at).toLocaleString()}
                        </Typography>
                      </Box>
                    </Box>
                    <Stack direction="row" spacing={1}>
                      <IconButton size="small">
                        <Visibility />
                      </IconButton>
                      <IconButton size="small">
                        <Download />
                      </IconButton>
                    </Stack>
                  </Box>
                </CardContent>
              </Card>
            ))}
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setVersionDialog(false)}>
            Close
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default ProjectDocumentsPage;