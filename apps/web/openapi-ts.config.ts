import { defineConfig } from '@hey-api/openapi-ts';

export default defineConfig({
  input: '../../services/api/openapi.json',
  output: {
    path: './src/lib/api/generated',
  },
  plugins: [
    '@hey-api/client-fetch',
  ],
});
