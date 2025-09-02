/**
 * Codemod: Auto-add missing Material UI imports (expanded)
 * Run with: npx jscodeshift -t scripts/add-mui-imports-v2.js frontend/src
 */
export default function transformer(file, api) {
  const j = api.jscodeshift;
  const root = j(file.source);

  // Expanded list from your latest logs
  const muiImports = [
    // Core
    'Alert', 'Dialog', 'DialogTitle', 'DialogContent', 'DialogActions',
    'CircularProgress', 'Paper', 'Container', 'Stack', 'Divider', 'Avatar',
    'Chip', 'Tooltip', 'CardContent', 'CardActions', 'LinearProgress',

    // Data input
    'TextField', 'Autocomplete', 'Select', 'MenuItem', 'MuiMenuItem',
    'Checkbox', 'Switch', 'InputAdornment',
    'FormControl', 'InputLabel', 'FormControlLabel', 'FormGroup',

    // Lists
    'List', 'ListItem', 'ListItemText', 'ListItemSecondaryAction',
    'ListItemIcon', 'ListItemAvatar',

    // Tabs
    'Tabs', 'Tab', 'TabPanel',

    // Tables
    'Table', 'TableHead', 'TableBody', 'TableRow', 'TableCell',
    'TableContainer',
  ];

  const existingImports = new Set();
  root.find(j.ImportDeclaration).forEach(path => {
    if (path.value.source.value.startsWith('@mui/material')) {
      path.value.specifiers.forEach(spec => {
        if (spec.imported) existingImports.add(spec.imported.name);
      });
    }
  });

  const used = new Set();
  root.find(j.JSXIdentifier).forEach(path => {
    used.add(path.value.name);
  });

  const missing = muiImports.filter(
    name => used.has(name) && !existingImports.has(name)
  );

  if (missing.length > 0) {
    const importDecl = j.importDeclaration(
      missing.map(name => j.importSpecifier(j.identifier(name))),
      j.literal('@mui/material')
    );
    root.get().node.program.body.unshift(importDecl);
  }

  return root.toSource();
}
