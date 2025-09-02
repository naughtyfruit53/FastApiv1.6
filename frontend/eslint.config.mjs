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
import unusedImports from 'eslint-plugin-unused-imports';

// Compute __dirname for ES modules
const __dirname = path.dirname(fileURLToPath(new URL('.', import.meta.url)));

export default [
  // ==== IGNORE BLOCK ====
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
      '**/*.d.ts',
      '**/.env*',
      '**/cypress/**',
      '**/playwright/**',
      '**/.storybook/**',
      '**/storybook-static/**',
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
      'unused-imports': unusedImports,
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
      // === AUTO-CLEAN UNUSED STUFF ===
      'unused-imports/no-unused-imports': 'error',
      'unused-imports/no-unused-vars': [
        'error',
        { vars: 'all', varsIgnorePattern: '^_', args: 'after-used', argsIgnorePattern: '^_' },
      ],

      // === RELAX RULES FOR DEPLOYMENT ===
      'no-unused-vars': 'off',
      '@typescript-eslint/no-unused-vars': 'off',
      'no-undef': 'off',
      'no-shadow': 'off',
      '@typescript-eslint/no-shadow': 'off',
      'no-use-before-define': 'off',
      'eqeqeq': 'off',
      '@typescript-eslint/explicit-module-boundary-types': 'off',
      '@typescript-eslint/no-empty-function': 'off',

      // === CRITICAL RULES (KEEP THESE) ===
      'react-hooks/rules-of-hooks': 'error',
      'react/jsx-no-undef': 'error',
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
      jest: { version: 30 },
    },
    rules: {
      ...jest.configs.recommended.rules,
    },
    languageOptions: {
      globals: { ...globals.jest },
    },
  },
];
