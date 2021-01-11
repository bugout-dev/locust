"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
var yargs_1 = __importDefault(require("yargs"));
var parse_1 = require("./parse");
var args = yargs_1.default(process.argv.slice(2))
    .usage("$0 -i [input_file] -o [output_file]")
    .option("i", {
    alias: "input",
    demandOption: true,
    type: "string",
})
    .option("o", {
    alias: "output",
    demandOption: false,
    type: "string",
}).argv;
parse_1.loadInput(args.i)
    .then(parse_1.definitionsByPatch)
    .then(function (results) { return parse_1.writeOutput(results, args.o); });
