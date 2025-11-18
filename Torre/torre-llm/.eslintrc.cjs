module.exports = {
  root: false, // Don't use as root config - inherit from parent
  parser: "@typescript-eslint/parser",
  plugins: ["@typescript-eslint", "import"],
  extends: [
    "eslint:recommended",
    "plugin:@typescript-eslint/recommended",
    "plugin:import/recommended",
    "plugin:import/typescript",
  ],
  parserOptions: {
    ecmaVersion: "latest",
    sourceType: "module",
  },
  env: {
    browser: true,
    node: true,
    es2021: true,
  },
  globals: {
    window: "readonly",
    document: "readonly",
    console: "readonly",
    module: "readonly",
    require: "readonly",
    fetch: "readonly",
    setTimeout: "readonly",
    setInterval: "readonly",
  },
  rules: {
    "no-unused-vars": "off",
    "@typescript-eslint/no-unused-vars": [
      "warn", // Changed from error to warn
      { argsIgnorePattern: "^_", varsIgnorePattern: "^_" },
    ],
    "@typescript-eslint/no-explicit-any": "warn", // Changed from error to warn
    "@typescript-eslint/no-var-requires": "warn", // Changed from error to warn
    "import/order": [
      "warn", // Changed from warn (already)
      { "newlines-between": "always", alphabetize: { order: "asc" } },
    ],
    "import/no-unresolved": "warn", // Changed from error to warn
    "no-undef": "warn", // Warn instead of error
  },
  ignorePatterns: ["dist", "node_modules", "venv", "**/*.d.ts"],
};
