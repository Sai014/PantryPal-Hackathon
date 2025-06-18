const mongoose = require('mongoose')

const NGOschema = new mongoose.Schema({
    name : String,
    location : {
        type : {type:String,enum: ["Point"]},
        coordinates : [Number]
    },
    contact : String 
})
NGOschema.index({location:'2dsphere'})
module.exports = mongoose.model("NGOs",NGOschema)