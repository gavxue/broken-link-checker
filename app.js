const express = require('express')
const { spawn } = require('child_process')
const path = require('path')

const app = express()

app.set('view engine', 'ejs')
app.set('views', path.join(__dirname, './views'))

app.use(express.static('public'))
app.use(express.urlencoded({ extended: true }))

app.get('/', (req, res) => {
    var dataset = []
    const python = spawn('python', ['main.py'])

    python.stdout.on('data', function (data) {
        console.log('piping data ...')
        dataset = String(data).split('\r\n')
    })

    python.on('close', (code) => {
        console.log(`closing with code ${code}`)
        res.render('index.ejs', { dataset })
    })
})

app.listen(process.env.PORT || 3000, () => {
    console.log('listening on port 3000')
})