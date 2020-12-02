const express = require('express')
const app = express()
const _assets = require('./js/assets')
const Joi = require('joi');
const { getPastSimulation, calculatePLBreakdown } = require('./js/calculateUserData')
const port = 3001

/* Parse request JSON body */
app.use(express.json());

/* Routes */
app.get('/assets', async (req, res, next) => {
    try {
        res.json(_assets)
    }
    catch (err) {
        next(err)
    }
})

app.post('/past_simulation', async (req, res, next) => {
    try {

        /* validate input */
        var schema = Joi.object({
            amountInvested: Joi.number().greater(0).required(),
            dateInvested: Joi.string().pattern(/[0-9]{4}-[0-9]{2}-[0-9]{2}/).required(),
            pool: Joi.string().required()
        })
        var { value, error } = schema.validate(req.body)
        if (error)
            return res.status(400).json({ err: error.details })
        if(new Date(value.dateInvested).getTime() > Date.now())
            return res.status(400).json({ err: `"dateInvested" value should be before today` })

        var simResult = await getPastSimulation(value.amountInvested, value.dateInvested, value.pool)
        var LPBreakdown = await calculatePLBreakdown(simResult)
        res.json({simResult, LPBreakdown})
    }
    catch (err) {
        next(err)
    }

})


/* Error response */
app.use(async (err, req, res, next) => {
    if (err.code && typeof err.code === "number") {
        console.error(err.message)
        res.status(err.code).json({ err: err.message })
    } else {
        console.error(err)
        console.log(err.stack)

        if (typeof e === "object")
            err = JSON.stringify(err)
        Notifier.reportBug("internal error: " + err)
        res.status(500).json({ msg: "internal error!" })
    }
});

app.listen(port, () => console.log(`Listening on port ${port}!`))

module.exports = app;
