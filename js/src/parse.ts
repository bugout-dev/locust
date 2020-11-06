import { promises as fsPromises, writeFileSync } from "fs";

import * as parser from "@babel/parser";
import traverse, { NodePath } from "@babel/traverse";
import * as babelTypes from "@babel/types";

// The JSON interfaces match the pydantic models in locust/git.py and locust/parse.py
interface LineInfo {
  old_line_number: number;
  new_line_number: number;
  line_type: string;
  line: string;
}

interface HunkBoundary {
  operation_type?: string;
  start: number;
  end: number;
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

interface DefinitionParent {
  name: string;
  line: number;
}

interface RawDefinition {
  name: string;
  change_type: string;
  line: number;
  offset: number;
  end_line?: number;
  end_offset?: number;
  parent?: DefinitionParent;
}

export async function loadInput(inputFile: string): Promise<GitResult> {
  const resultBuffer: Buffer = await fsPromises.readFile(inputFile);
  const resultString: string = resultBuffer.toString();
  const result: GitResult = JSON.parse(resultString);
  return result;
}

// getDefinitions replicates the logic of the AST visit functions from the LocustVisitor class in
// the Locust python parser.
export function getDefinitions(
  source: string,
  sourceFilename: string
): Array<RawDefinition> {
  if (!source) {
    return [];
  }

  let definitions: Array<RawDefinition> = [];
  let scope: Array<[string, number, number?]> = [];

  const ast: babelTypes.File = parser.parse(source, {
    sourceFilename,
    plugins: ["classPrivateMethods", "jsx", "typescript"],
  });

  function processDeclaration(
    path:
      | NodePath<babelTypes.FunctionDeclaration>
      | NodePath<babelTypes.ClassDeclaration>
      | NodePath<babelTypes.ClassMethod>
      | NodePath<babelTypes.ClassPrivateMethod>,
    definitionType: string
  ): void {
    const node = path.node;
    let idNode: babelTypes.Identifier | null = null;
    if (node.type === "ClassPrivateMethod") {
      idNode = node.key.id;
    } else if (node.type === "ClassMethod") {
      idNode = node.key as babelTypes.Identifier;
    } else {
      idNode = node.id;
    }
    if (!idNode || !node.loc) {
      path.skip();
    } else {
      const startLine = node.loc.start.line;
      const startColumn = node.loc.start.column;
      const endLine = node.loc.end.line;
      const endColumn = node.loc.end.column;

      scope = scope.filter((item) => item[2] && item[2] > startLine);

      let parent: DefinitionParent | undefined = undefined;
      if (scope.length) {
        const scopeParent = scope[scope.length - 1];
        parent = { name: scopeParent[0], line: scopeParent[1] };
      }
      let name = idNode.name;
      if (parent) {
        name = `${parent.name}.${name}`;
      }
      const definition: RawDefinition = {
        name,
        change_type: definitionType,
        line: startLine,
        offset: startColumn,
        end_line: endLine,
        end_offset: endColumn,
        parent,
      };
      definitions.push(definition);
      scope.push([name, node.loc?.start.line, node.loc?.end.line]);
    }
  }

  traverse(ast, {
    // For now, we skip all anonymous functions
    FunctionExpression: function (path) {
      path.skip();
    },
    FunctionDeclaration: function (path) {
      processDeclaration(path, "function");
    },
    ClassExpression: function (path) {
      path.skip();
    },
    ClassDeclaration: function (path) {
      processDeclaration(path, "class");
    },
    ClassMethod: function (path) {
      processDeclaration(path, "method");
    },
    ClassPrivateMethod: function (path) {
      processDeclaration(path, "method");
    },
  });

  return definitions;
}

export function definitionsForPatch(patch: PatchInfo): Array<RawDefinition> {
  const source = patch.new_source;
  if (!source) {
    return [];
  }
  const definitions = getDefinitions(source, patch.new_file);
  return definitions;
}

export function definitionsByPatch(
  result: GitResult
): Array<[PatchInfo, Array<RawDefinition>]> {
  return result.patches
    .filter((patch) => patch.new_file.split(".").pop() === "js")
    .map((patch) => [patch, definitionsForPatch(patch)]);
}

export function writeOutput(
  patchDefinitions: Array<[PatchInfo, Array<RawDefinition>]>,
  outfile?: string
): void {
  const output = JSON.stringify(patchDefinitions);
  if (!outfile) {
    console.log(output);
  } else {
    writeFileSync(outfile, output);
  }
}
