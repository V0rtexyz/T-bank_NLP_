# T-Plexity Frontend - Установка без прав администратора

## Проблема
У вас нет установленного Node.js и нет прав sudo для установки через apt.

## Решение: Установка через NVM (Node Version Manager)

NVM позволяет установить Node.js локально в вашу домашнюю директорию без прав администратора.

---

## Быстрая установка

### Шаг 1: Установите Node.js через наш скрипт

```bash
cd /srv/nlp1/eval_dir/T-bank_NLP_/frontend
chmod +x install-node.sh
./install-node.sh
```

### Шаг 2: Перезагрузите shell

```bash
source ~/.bashrc
# или
source ~/.zshrc  # если используете zsh
```

### Шаг 3: Проверьте установку

```bash
node --version   # должно показать v20.x.x
npm --version    # должно показать 10.x.x
```

### Шаг 4: Установите зависимости проекта

```bash
npm install
```

### Шаг 5: Запустите dev-сервер

```bash
npm run dev
```

Приложение будет доступно на `http://localhost:3000`

---

## Ручная установка (если скрипт не работает)

### 1. Установите NVM

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
```

### 2. Загрузите NVM в текущую сессию

```bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
```

### 3. Установите Node.js 20 LTS

```bash
nvm install 20
nvm use 20
nvm alias default 20
```

### 4. Проверьте установку

```bash
node --version
npm --version
```

### 5. Установите зависимости

```bash
cd /srv/nlp1/eval_dir/T-bank_NLP_/frontend
npm install
```

### 6. Запустите приложение

```bash
npm run dev
```

---

## Альтернатива: Docker (если есть Docker)

Если на сервере установлен Docker, можно использовать контейнеризацию:

### Запуск в dev-режиме

```bash
docker run -it --rm \
  -v $(pwd):/app \
  -w /app \
  -p 3000:5173 \
  node:20-alpine \
  sh -c "npm install && npm run dev -- --host"
```

### Или используйте docker-compose

Создайте `docker-compose.yml`:

```yaml
version: '3.8'

services:
  frontend:
    image: node:20-alpine
    working_dir: /app
    volumes:
      - .:/app
      - node_modules:/app/node_modules
    ports:
      - "3000:5173"
    command: sh -c "npm install && npm run dev -- --host"
    environment:
      - VITE_API_URL=http://localhost:8000/api

volumes:
  node_modules:
```

Затем запустите:

```bash
docker-compose up
```

---

## Альтернатива: Использование готового билда

Если вам нужен только production build, можно использовать Docker для сборки:

### 1. Соберите образ

```bash
cd /srv/nlp1/eval_dir/T-bank_NLP_/frontend
docker build -t tplexity-frontend .
```

### 2. Запустите контейнер

```bash
docker run -d -p 3000:80 --name tplexity-frontend tplexity-frontend
```

### 3. Откройте в браузере

```
http://localhost:3000
```

---

## Проверка установки

После успешной установки вы должны увидеть:

```bash
$ node --version
v20.11.0

$ npm --version
10.2.4

$ npm run dev

  VITE v5.1.4  ready in 324 ms

  ➜  Local:   http://localhost:3000/
  ➜  Network: use --host to expose
  ➜  press h to show help
```

---

## Устранение проблем

### Ошибка: "command not found" после установки NVM

**Решение**: Перезагрузите shell или выполните:

```bash
source ~/.bashrc
```

### Ошибка: "npm install" падает с ошибкой памяти

**Решение**: Увеличьте лимит памяти для Node.js:

```bash
export NODE_OPTIONS="--max-old-space-size=4096"
npm install
```

### Порт 3000 уже занят

**Решение**: Используйте другой порт:

```bash
npm run dev -- --port 3001
```

### NVM не загружается автоматически

**Решение**: Добавьте в `~/.bashrc` или `~/.zshrc`:

```bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"
```

---

## Команды для разработки

```bash
# Установка зависимостей
npm install

# Запуск dev-сервера
npm run dev

# Сборка для production
npm run build

# Просмотр production build локально
npm run preview

# Проверка кода (linting)
npm run lint
```

---

## Системные требования

- **Память**: Минимум 2GB RAM (рекомендуется 4GB)
- **Диск**: ~500MB для node_modules
- **Процессор**: Любой современный CPU
- **ОС**: Linux, macOS, Windows (WSL)

---

## Полезные ссылки

- [NVM GitHub](https://github.com/nvm-sh/nvm)
- [Node.js Documentation](https://nodejs.org/)
- [Vite Documentation](https://vitejs.dev/)
- [React Documentation](https://react.dev/)

---

## Поддержка

Если возникли проблемы, проверьте:

1. ✅ NVM установлен: `command -v nvm`
2. ✅ Node.js доступен: `node --version`
3. ✅ npm доступен: `npm --version`
4. ✅ В `~/.bashrc` есть настройки NVM

При сохраняющихся проблемах используйте Docker-решение.

