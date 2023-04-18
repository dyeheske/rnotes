
# `Dummy tool` - `v0.2`

## Highlights
  * **Added the support for MI RTL grouping, by adding the relevant NocStudio commands to the NCF writer, and implemented the algorithm of MI.**
  * **Added the support for part select in clock automation, that required some changes in the tree shaped spec too. This new infrastructure will also effect other automations that uses tree shaped specs.**


## SideBand automation
  * ### Bugs:
    * [[71121](https://hsdes.intel.com/appstore/article/#/12345)]: **NocStudio failed on out of memory error when using the generated NCF file**  
      The issue happened because many calls to gen_image function that it is highly memory consumer. Changed this so we will use this function only when debug mode is on.  

    * [[72415](https://hsdes.intel.com/appstore/article/#/72415)]: **Bug in ncf writer when setting the flag uturn to False**  
      Fixed a bug in NCF writer, that happened because of a missing argument to a function, that should be provided to the Writer function.  

  * ### Enhancements:
    * [[28543](https://hsdes.intel.com/appstore/article/#/28543)]: **Need the support for MI of RTL grouping**  
      Added the support for MI RTL grouping, by adding the relevant NocStudio commands to the NCF writer, and implemented the algorithm of MI.  

      ![image](https://user-images.githubusercontent.com/89130737/232465301-be37ce13-2eb7-4890-a8e7-6a359d165d07.png)


## Clock automation
  * ### Bugs:
    * [[12345](https://hsdes.intel.com/appstore/article/#/12345)]: **Clock automation failed to do tie offs connections**  
      The root cause for this issue is a bug in the code that doing the tie offs, so a corner happened when the tie off value was not match to the dimensions of the clock port.  

  * ### Enhancements:
    * [[44354](https://hsdes.intel.com/appstore/article/#/44354)]: **Need the support for part select in clock automation**  
      Added the support for part select in clock automation, that required some changes in the tree shaped spec too. This new infrastructure will also effect other automations that uses tree shaped specs.  

    * [[72352](https://hsdes.intel.com/appstore/article/#/72352)]: **Clock automation need to support divided clocks**  
      Added the support of divided clocks to clock automation that required a major changes in the infra rules file.  


## Reset automation
  * ### Enhancements:
    * [[11216](https://hsdes.intel.com/appstore/article/#/11216)]: **Need the support for Phases that dont need reset widgets insertion**  
      Added the support of phases that will do the connectivity as is, without inserting any reset widgets nodes to the reset spec.  

    * [[24412](https://hsdes.intel.com/appstore/article/#/24412)]: **Need a support for both cold and warm reset phases**  
      Added the support for cold and warm reset.  

  * ### Performances:
    * [[13481](https://hsdes.intel.com/appstore/article/#/13481)]: **Reset automation hang after in the latest version**  
      Reduced the total runtime of the reset automation, by changing the search terms to more efficient search terms, so for the given test case, it took almost half of the time, 2 minutes instead of 15 minutes  


## Catalog
  * ### Performances:
    * [[no ticket](https://github.com/dyeheske/dummy_tool)]: **NA**  
      Added parallel loading of the catalog, so every Python file of IP will be converted to pickle file, for caching, using 80 percent of all the available cores.  

      ![image](https://user-images.githubusercontent.com/89130737/232479499-5133ea94-0ca2-42c2-8840-64089703a7fb.png)


## Other
  * ### Enhancements:
    * [[no ticket](https://github.com/dyeheske/dummy_tool)]: **NA**  
      Added interactive Jupyter notebooks, to allow the user adding IP catalog to the contour more easily than using CLI.  


### User guide:
  * [Dummy tool user guide - Intel Enterprise Wiki](https://wiki.ith.intel.com/display/ITSsocks/Dummy+Tool)

### For more information, contact:
  * Dor Yeheskel: dor.yeheskel@intel.com
  * Tom Jobim: tom.jobim@intel.com
  * Joao Gilberto: joao.gilberto@intel.com
