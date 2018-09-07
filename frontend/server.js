const express = require('express')
const next = require('next')
const path = require('path')
const compression = require('compression')

const dev = process.env.NODE_ENV !== 'production'
const app = next({ dev })
const routes = require('./routes')
const handler = routes.getRequestHandler(app)


app.prepare()
.then(() => {
  const server = express()
  server.use(compression())  //

  // robots txt
  server.get('/robots.txt', (req, res) => {
    res.sendFile(
      path.join(
        __dirname,
        './static',
        dev ? 'robots-dev.txt': 'robots.txt'
      ))
  })

  server.get('*', (req, res) => {
    return handler(req, res)
  })

  server.listen(3000, (err) => {
    if (err) throw err
    console.log('> Ready on http://localhost:3000')
  })
})
.catch((ex) => {
  console.error(ex.stack)
  process.exit(1)
})