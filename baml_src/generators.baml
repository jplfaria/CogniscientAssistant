// BAML Generator Configuration
// This file configures how BAML generates client code

generator python {
  output_type "python/pydantic"
  output_dir "../baml_client"
  version "0.90.2"
}

// Future generator configurations can be added here
// For example:
// generator typescript {
//   output_type "typescript"
//   output_dir "../baml_client_ts"
// }