#!/usr/bin/env bash
# wizard.sh: retired.
#
# This script used to wire a `loci-mcp` server into Claude Desktop. That server
# shipped inside the loci desktop app, which is now archived. This stub writes
# nothing and changes no config; it only prints the current way in.
#
# Source: https://github.com/huximaxi/loci

cat <<'MSG'

loci: the MCP installer is retired. Nothing was installed or changed.

loci is plain text now. To start:

  git clone https://github.com/huximaxi/loci
  cp -r loci/templates ./palace

Then open loci/FIRST-SESSION.md with any file-aware AI in that folder. The
first session builds palace/PALACE.md. No server, no port, nothing leaves
your machine.

If an earlier run of this script added a "loci" entry under mcpServers in
your Claude Desktop config, you can delete that entry; nothing serves it.

MSG
exit 1
