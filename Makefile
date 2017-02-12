PLUGIN=$(shell basename ${PWD})
PLUGIN_ZIP=$(PLUGIN).zip
PUSH_DIR=/sdcard/Download/

package: clean
	mkdir $(PLUGIN)
	rsync -a . $(PLUGIN) --exclude $(PLUGIN)
	zip -r $(PLUGIN_ZIP) $(PLUGIN) -x $(PLUGIN)/.git\*
	rm -rf $(PLUGIN)

clean:
	rm -f $(PLUGIN_ZIP)

push: package
	adb push $(PLUGIN_ZIP) $(PUSH_DIR)
