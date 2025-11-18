module.exports = {
  root: true,
  env: {
    browser: true,
    es2021: true,
    node: true,
  },
  extends: ["eslint:recommended"],
  parserOptions: {
    ecmaVersion: "latest",
    sourceType: "module",
  },
  globals: {
    // Browser globals
    window: "readonly",
    document: "readonly",
    console: "readonly",
    fetch: "readonly",
    setTimeout: "readonly",
    setInterval: "readonly",
    // Node.js globals
    module: "readonly",
    require: "readonly",
    __dirname: "readonly",
    __filename: "readonly",
    process: "readonly",
    // k6 globals
    __ENV: "readonly",
    // Emscripten/WebWorker globals
    self: "readonly",
    TextEncoder: "readonly",
    // Event globals
    event: "readonly",
  },
  ignorePatterns: [
    "node_modules/",
    "venv/",
    ".vercel/",
    "dist/",
    "build/",
    "**/*.d.ts",
    "Torre/torre-llm/venv/",
    "Torre/torre-llm/node_modules/",
    "Torre/torre-llm/dist/",
  ],
  rules: {
    "no-unused-vars": [
      "warn",
      {
        argsIgnorePattern: "^_",
        varsIgnorePattern: "^_",
      },
    ],
    "no-console": "off",
    "no-undef": "warn", // Warn instead of error for files without proper env config
    "no-empty": "warn",
    "no-constant-condition": "warn",
  },
  overrides: [
    {
      files: [
        "**/*.js",
        "**/extension.js",
        "**/*.cjs",
        "**/torre-extension/**/*.js",
      ],
      env: {
        node: true,
        browser: true,
      },
      rules: {
        "no-undef": "warn", // Warn instead of error for extension files
        "@typescript-eslint/no-var-requires": "off", // Allow require() in JS extension files
      },
    },
    {
      files: ["**/jest.config.js", "**/eslint.config.js"],
      env: {
        node: true,
      },
    },
    {
      files: ["scripts/k6/**/*.js"],
      env: {
        node: false,
      },
      globals: {
        __ENV: "readonly",
      },
    },
    {
      files: ["Torre/torre-llm/**/*.{ts,tsx}"],
      rules: {
        "import/no-unresolved": "off", // Torre has its own ESLint config with proper path resolution
      },
    },
    {
      files: [
        "Torre/torre-llm/**/*.js",
        "Torre/torre-llm/**/*.cjs",
        "Torre/torre-llm/torre-extension/**/*.js",
      ],
      env: {
        node: true,
        browser: true,
      },
      rules: {
        "@typescript-eslint/no-var-requires": "off", // Allow require() in JS files
        "no-undef": "off", // Torre JS files have their own config
        "no-unused-vars": "off", // Allow unused vars in extension files
      },
    },
    {
      files: [
        "Torre/torre-llm/extensions/vscode/**/*.ts",
        "Torre/torre-llm/tools/codemods/**/*.ts",
      ],
      rules: {
        "import/no-unresolved": "off", // VSCode and ts-morph are external dependencies
      },
    },
    {
      files: ["Torre/torre-llm/tools/testgen/**/*.ts"],
      rules: {
        "import/no-unresolved": "off", // Template files with placeholder imports
      },
    },
    {
      files: [
        "Torre/torre-llm/tools/testgen/**/*.ts",
        "Torre/torre-llm/demo_fix_test.ts",
        "Torre/torre-llm/test_file_with_error.js",
      ],
      rules: {
        "import/no-unresolved": "off", // Test/demo files with intentional errors
        "@typescript-eslint/no-unused-vars": "off", // Test files with intentional unused vars
        "no-undef": "off", // Test files with intentional undefined vars
        "no-constant-condition": "off", // Test files with intentional constant conditions
      },
    },
    {
      files: ["Torre/torre-llm/venv/**/*", "Torre/torre-llm/node_modules/**/*"],
      rules: {
        "import/no-unresolved": "off", // Ignore third-party code
        "no-undef": "off",
      },
    },
  ],
};
