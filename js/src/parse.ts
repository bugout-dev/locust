import { promises as fsPromises } from "fs";

import * as parser from "@babel/parser";
import * as babelTypes from "@babel/types";

// The JSON interfaces match the pydantic models in locust/git.py and locust/parse.py
interface LineInfo {
  old_line_number: bigint;
  new_line_number: bigint;
  line_type: string;
  line: string;
}

interface HunkBoundary {
  operation_type?: string;
  start: bigint;
  end: bigint;
}

interface HunkInfo {
  header: string;
  lines: Array<LineInfo>;
  total_boundary?: HunkBoundary;
  insertions_boundary?: HunkBoundary;
  deletions_boundary?: HunkBoundary;
}

interface PatchInfo {
  old_file: string;
  new_file: string;
  hunks: Array<HunkInfo>;
  old_source?: string;
  new_source?: string;
}

interface GitResult {
  repo: string;
  initial_ref: string;
  terminal_ref?: string;
  patches: Array<PatchInfo>;
}

interface RawDefinition {
  name: string;
  change_type: string;
  line: bigint;
  offset: bigint;
  end_line?: bigint;
  end_offset?: bigint;
  parent?: [string, bigint];
}

interface LocustChange {
  name: string;
  change_type: string;
  filepath: string;
  revision?: string;
  line: bigint;
  changed_lines: bigint;
  total_lines?: bigint;
  parent?: [string, bigint];
}

export async function loadInput(inputFile: string): Promise<GitResult> {
  const resultBuffer: Buffer = await fsPromises.readFile(inputFile);
  const resultString: string = resultBuffer.toString();
  const result: GitResult = JSON.parse(resultString);
  return result;
}

export async function locustChanges(result: GitResult): Promise<null> {
  console.log(result);
  const patch = result.patches[0];
  const source = patch.new_source;
  if (source) {
    const ast: babelTypes.File = parser.parse(source, {
      sourceFilename: patch.new_file,
    });
    console.log(ast.program);
  }

  return null;
}
