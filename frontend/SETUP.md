# Frontend Setup Guide

## Node.js Installation

Node.js and npm have been installed using **nvm** (Node Version Manager) in your home directory.

### Using nvm in new terminal sessions

When you open a new terminal, you need to load nvm first:

```bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
```

Or simply add this to your `~/.bashrc` (it should already be there after nvm installation).

### Current versions

- **Node.js**: v24.11.1 (LTS)
- **npm**: v11.6.2

### Running the development server

```bash
cd frontend
export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
npm run dev
```

The app will be available at `http://localhost:3000`

### Useful nvm commands

```bash
# List installed Node.js versions
nvm list

# Install a specific version
nvm install 20

# Use a specific version
nvm use 20

# Set default version
nvm alias default 20
```

### Note

The deprecation warnings during `npm install` are normal and don't affect functionality. You can run `npm audit fix` to address security vulnerabilities if needed.


