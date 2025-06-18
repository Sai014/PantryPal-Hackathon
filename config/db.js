const mongoose = require('mongoose')
require('dotenv').config();
console.log(process.env.MONGO_URI)
const connectDB = async () =>{
    try{
        await mongoose.connect(process.env.MONGO_URI,{
            useNewUrlParser : true,
            useUnifiedTopology : true
        });
        console.log('MONGOOSE CONNECTED')
    }
    catch(err){
        console.log("COULD NOT CONNECT",err)
        process.exit(1)
    }
}
module.exports = connectDB


