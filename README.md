swviz: Software Visualizer

What is swviz?
The primary purpose of swviz is to generate accurate call-graph of entire program and be able to query and view it with ease.

How does it work?
swviz uses Clang to generate call-graph for individual source files. Apply this patch to clang:
http://git.linuxfoundation.org/?p=llvmlinux.git;a=blob;f=toolchain/clang/patches/llvm/call_graph.patch

To generate the full program call-graph we stitch together call-graphs of these individual files together. The idea is to
invoke the graph-stitching from the linker. That way, we can piggyback on the linker's capability to resolve symbols and stitch the
individual files call-graphs appropriately. We're using MCLINKER to work with swviz.

How to make swviz work?
After applying the above Clang patch and compiling, .dot files would be output alongside .o files. Then to stitch together the call-graphs together,
invoke process_graph.py with these input dot files and an output file.
Create a django project and plug in the views.py, graphAnalyzer.py and urls.py and load this .dot file in the django app in views.py.
Use the app.js and index.html to view and query the call-graph loaded.

This is a proof of concept currently. Full functionality with integration with Linker is a work in progress.