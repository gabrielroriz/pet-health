FROM node:22-slim

WORKDIR /code
RUN chown node:node /code
USER node

COPY --chown=node:node package.json yarn.lock ./
RUN yarn install --frozen-lockfile

COPY --chown=node:node . .

EXPOSE 5173

# Serve the app with the Vite dev server for local development.
CMD ["yarn", "dev", "--host", "0.0.0.0"]
