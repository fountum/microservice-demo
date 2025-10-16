# auth/nodejs
# reference: https://www.digitalocean.com/community/tutorials/how-to-build-a-node-js-application-with-docker#step-3-writing-the-dockerfile
FROM node:22-alpine
# create directories for user "node"
# do this to ensure we have permissions
RUN mkdir -p /home/node/app/node_modules && chown -R node:node /home/node/app
# set working dir of app
WORKDIR /home/node/app
# copy package.json and package-lock.json
COPY package*.json ./
# switching to user "node"; provided by node image
USER node
# app setup
RUN npm install
# copy app code
COPY --chown=node:node . .

EXPOSE 3001

CMD [ "node", "index.js" ]
