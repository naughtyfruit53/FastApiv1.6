import js from '@eslint/js';
import tsEslint from '@typescript-eslint/eslint-plugin';
import tsParser from '@typescript-eslint/parser';
import reactHooks from 'eslint-plugin-react-hooks';
import reactPlugin from 'eslint-plugin-react';
import nextPlugin from '@next/eslint-plugin-next';
import jest from 'eslint-plugin-jest';
import globals from 'globals';
import path from 'path';
import { fileURLToPath } from 'url';

// Compute __dirname for ES modules
const __dirname = path.dirname(fileURLToPath(new URL('.', import.meta.url)));

export default [
  // ==== IGNORE BLOCK: Add all your ignored paths here ====
  {
    ignores: [
      '**/node_modules/**',
      '**/dist/**',
      '**/build/**',
      '**/.next/**',
      '**/coverage/**',
      '**/.turbo/**',
      '**/out/**',
      '**/public/**',
      '**/.cache/**',
      '**/.eslintcache',
      '**/*.d.ts', // Optionally ignore all type definition files
      '**/.env*',
      '**/cypress/**',
      '**/playwright/**',
      '**/.storybook/**',
      '**/storybook-static/**',
      // Add any other generated or legacy folders you want to ignore
    ],
  },

  // ==== MAIN CONFIG FOR TS/TSX ====
  {
    files: ['**/*.ts', '**/*.tsx'],
    plugins: {
      '@typescript-eslint': tsEslint,
      'react-hooks': reactHooks,
      'react': reactPlugin,
      '@next/next': nextPlugin,
    },
    languageOptions: {
      parser: tsParser,
      parserOptions: {
        ecmaFeatures: { jsx: true },
        ecmaVersion: 2021,
        sourceType: 'module',
        project: './tsconfig.json',
      },
      globals: {
        ...globals.browser,
        console: 'readonly',
        fetch: 'readonly',
        localStorage: 'readonly',
        window: 'readonly',
        document: 'readonly',
        setTimeout: 'readonly',
        alert: 'readonly',
        process: 'readonly',
        atob: 'readonly',
      },
    },
    rules: {
      // JavaScript rules
      'no-unused-vars': 'error',
      'no-undef': 'error',
      'eqeqeq': ['error', 'always'],
      'curly': ['error', 'all'],
      'no-redeclare': 'error',
      'no-shadow': 'error',
      'no-use-before-define': ['error', { functions: false, classes: false }],
      // TypeScript-specific rules
      '@typescript-eslint/no-explicit-any': 'off',
      '@typescript-eslint/no-unused-vars': 'off', // Can turn on after cleanup
      '@typescript-eslint/explicit-module-boundary-types': 'error',
      '@typescript-eslint/no-shadow': 'error',
      '@typescript-eslint/no-empty-function': 'error',
      '@typescript-eslint/no-unused-expressions': 'error',
      // React-specific rules
      'react-hooks/exhaustive-deps': 'off',
      'react-hooks/rules-of-hooks': 'error',
      'react/jsx-no-undef': 'error',
      'react/no-unescaped-entities': 'off',
      // General JavaScript rules
      'no-useless-escape': 'off',
      'no-console': 'off',
      // Next.js-specific rules
      '@next/next/no-document-import-in-page': 'error',
      '@next/next/no-img-element': 'error',
      '@next/next/no-sync-scripts': 'error',
    },
  },

  // ==== OVERRIDE: routes.d.ts ====
  {
    files: ['.next/types/routes.d.ts'],
    rules: {
      '@typescript-eslint/no-empty-object-type': 'off',
    },
  },

  // ==== TEST FILES ====
  {
    files: ['**/__tests__/**/*.[jt]s?(x)', '**/?(*.)+(spec|test).[jt]s?(x)'],
    plugins: { jest },
    settings: {
      jest: {
        version: 30,
      },
    },
    rules: {
      ...jest.configs.recommended.rules,
    },
    languageOptions: {
      globals: {
        ...globals.jest,
      },
    },
  },
];