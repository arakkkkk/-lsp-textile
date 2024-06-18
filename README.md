# textilels
An implementation of the Language Server Protocol for textile.
## Instration
```
pip install git+https://github.com/arakkkkk/textilels
```

## Usage
For neovim

```lua
vim.api.nvim_create_autocmd({ "BufNewFile", "BufRead" }, {
	pattern = "*.tt",
	callback = function()
		vim.bo.filetype = "textile"
	end,
})

local lspconfig = require("lspconfig")
local configs = require("lspconfig.configs")

if not configs.textilels then
	configs.textilels = {
		default_config = {
			-- cmd = { "nargo", "lsp" },
			cmd = { "textilels" },
			-- cmd = { "python", "/home/arakkk/Downloads/lsp-textile/pygls/lsp-textile.py" },
			root_dir = lspconfig.util.root_pattern("*"),
			-- root_dir = vim.fn.getcwd(), -- Use PWD as project root dir.
			filetypes = { "textile" },
		},
	}
end
lspconfig.textilels.setup({})

```

