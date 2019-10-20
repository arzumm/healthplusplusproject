const mongoose = require('mongoose');

const entrySchema = new mongoose.Schema({
  name: {type: String, required: true}, 
  completed:{type: Boolean, default: false}
});

const Entry = mongoose.model('Entry', entrySchema);

module.exports = Entry;