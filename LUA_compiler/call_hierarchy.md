### Call hierarchy of the "model" function
```py
model
  grammar_get_chunk 1
    grammar_get_block 1
      try_block_statement 1
        grammar_get_statement 1
          try_statement 2
            try_statement_semicolon 1
            try_statement_assignment 2
              grammar_get_varlist 1
                grammar_get_var 2
                  try_var 1
                    try_var_prefix_name 1
                      grammar_get_prefixexp 1
                        try_prefixexp 2
                          try_prefixexp_var 1
                 |----------*grammar_get_var*
                          try_prefixexp_exp 1
                            grammar_get_exp 1
                              try_exp 9
                                try_exp_prefixexp 1
                       |----------*grammar_get_prefixexp*
                                try_exp_binop 2
                             |----*grammar_get_exp*
                             |----*grammar_get_exp*
                                try_exp_nil 0
                                try_exp_true 0
                                try_exp_false 0
                                try_exp_number 0
                                try_exp_string 0
                                try_exp_ellipsis 0
                                try_exp_unop 1
                             |----*grammar_get_exp*
                    try_var_name 0
              grammar_get_explist 1
                grammar_get_exp 1
                  try_exp 9
                    try_exp_prefixexp 1
                      grammar_get_prefixexp 1
                        try_prefixexp 1
                          try_prefixexp_var 2
                            grammar_get_var 1
                              try_var 1
                                try_var_prefix_name 1
                       |----------*grammar_get_prefixexp*
                          try_prefixexp_exp 1
                 |----------*grammar_get_exp*
                    try_exp_binop 2
                 |----*grammar_get_exp*
                 |----*grammar_get_exp*
                    try_exp_nil 0
                    try_exp_true 0
                    try_exp_false 0
                    try_exp_number 0
                    try_exp_string 0
                    try_exp_ellipsis 0
                    try_exp_unop 1
                 |----*grammar_get_exp*

- Number of loops: 9
- Deepest nesting: 17
- Maximum branching: 9
- Terminating branches: 9 (only expressions)
```