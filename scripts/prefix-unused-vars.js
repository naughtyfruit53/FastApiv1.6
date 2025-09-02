/**
 * Codemod: Prefix unused useState variables/setters with _
 * Run with: npx jscodeshift -t scripts/prefix-state-vars.js frontend/src
 */
export default function transformer(file, api) {
  const j = api.jscodeshift;
  const root = j(file.source);

  // Match useState calls
  root.find(j.VariableDeclarator, {
    init: { callee: { name: 'useState' } }
  }).forEach(path => {
    if (path.value.id.type === 'ArrayPattern') {
      const [state, setter] = path.value.id.elements;
      if (state && state.name && !state.name.startsWith('_')) {
        state.name = `_${state.name}`;
      }
      if (setter && setter.name && !setter.name.startsWith('_')) {
        setter.name = `_${setter.name}`;
      }
    }
  });

  return root.toSource();
}
