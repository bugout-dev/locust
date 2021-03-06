import yargs from "yargs";

import { loadInput, definitionsByPatch, writeOutput } from "./parse";

const args = yargs(process.argv.slice(2))
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

loadInput(args.i)
  .then(definitionsByPatch)
  .then((results) => writeOutput(results, args.o));
