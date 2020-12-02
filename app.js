const express = require('express')
const app = express()
const _assets = require('./js/assets')

const port = 3001

/* Parse request JSON body */
app.use(express.json());

/* Routes */
app.get('/assets', async (req, res, next)=>{
    try{
        res.json(_assets)
    }
    catch(err){
        next(err)
    }
})
// app.use('/menu', require('./routes/menu'));


/* Error response */
app.use(async (err, req, res, next) => {
    if (err.code && typeof err.code === "number") {
        console.error(err.message)
        res.status(err.code).json({err: err.message})
    } else {
        console.error(err)
        console.log(err.stack)

        if(typeof e === "object")
            err = JSON.stringify(err)
        Notifier.reportBug("internal error: " + err)
        res.status(500).json({msg: "internal error!"})
    }
});

app.listen(port, () => console.log(`Listening on port ${port}!`))

module.exports = app;
