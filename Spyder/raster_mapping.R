require(sf) # simple features - geoprocessing functions and mor
require(raster)

setwd(dirname(rstudioapi::getActiveDocumentContext()$path))

klein <- T
examplesTF <- T
vorher <- F
cop_comparison <- F

size <- "big"

# z.b der Abbildungsname aus der tabelle
# KEINE ZAHL REIN!!!
collection_name <- "ms_big_random"

r1 <- raster("D:/Bachelorarbeit/Project/Data/Damage_Assessment/satellite/mhk_b_clipped.tif", band=1)
r2 <- raster("D:/Bachelorarbeit/Project/Data/Damage_Assessment/satellite/mhk_b_clipped.tif", band=2)
r3 <- raster("D:/Bachelorarbeit/Project/Data/Damage_Assessment/satellite/mhk_b_clipped.tif", band=3)

if (klein){
  r1 <- raster("D:/Bachelorarbeit/Project/Data/Damage_Assessment/satellite/mir_b.tif", band=1)
  r2 <- raster("D:/Bachelorarbeit/Project/Data/Damage_Assessment/satellite/mir_b.tif", band=2)
  r3 <- raster("D:/Bachelorarbeit/Project/Data/Damage_Assessment/satellite/mir_b.tif", band=3)
  
  collection_name <- "ms_small_random"
  size <- "small"
}

if (vorher){
  r1 <- raster("D:/Bachelorarbeit/Project/Data/Damage_Assessment/satellite/test4.tif", band=1)
  r2 <- raster("D:/Bachelorarbeit/Project/Data/Damage_Assessment/satellite/test4.tif", band=2)
  r3 <- raster("D:/Bachelorarbeit/Project/Data/Damage_Assessment/satellite/test4.tif", band=3)
  
}

rgb <- stack(list(r1, r2, r3))

clips <- list(NULL, NULL, NULL, NULL)

four_examples <- function(){
  examples <- read_sf(dsn = "D:/Bachelorarbeit/Project/Spyder/outputs/collections/random_sample_collection", layer="random_sample_collection")
  examples <- st_transform(examples, 32618)

  
  if (cop_comparison){
    ex1 <- crop(rgb, examples[examples$random_cho == 'both',])
    ex2 <- crop(rgb, examples[examples$random_cho == 'only_cop',])
    ex3 <- crop(rgb, examples[examples$random_cho == 'only_ms',])
    ex4 <- crop(rgb, examples[examples$random_cho == 'both_not',])
    
    id1 <- examples[examples$random_cho == 'both',]['idx'][[1]]
    id2 <- examples[examples$random_cho == 'only_cop',]['idx'][[1]]
    id3 <- examples[examples$random_cho == 'only_ms',]['idx'][[1]]
    id4 <- examples[examples$random_cho == 'both_not',]['idx'][[1]]
    
    file1 <- paste('outputs/rasters/',collection_name,'_exa_',id1, '.tif', sep="")
    file2 <- paste('outputs/rasters/',collection_name,'_exb_',id2, '.tif', sep="")
    file3 <- paste('outputs/rasters/',collection_name,'_exc_',id3, '.tif', sep="")
    file4 <- paste('outputs/rasters/',collection_name,'_exd_',id4, '.tif', sep="")
    
    writeRaster(ex1, file1, overwrite=TRUE)
    writeRaster(ex2, file2, overwrite=TRUE)
    writeRaster(ex3, file3, overwrite=TRUE)
    writeRaster(ex4, file4, overwrite=TRUE)
  }
}


four_examples()

make_example <- function(x){
  # browser()
  ex1 <- crop(rgb, x$geometry[[1]])
  id1 <- x['idx'][[1]]
  file1 <- paste('outputs/rasters/',collection_name,id1, '.tif', sep="")
  writeRaster(ex1, file1, overwrite=TRUE)
  
}

if (examplesTF){
  name <- "ms_big_copfür_kleiner"
  
  examples <- read_sf(dsn = "D:/Bachelorarbeit/Project/Spyder/outputs/examples", layer=name)
  examples <- st_transform(examples, crs(rgb))
  
  collection_name <- paste("ms", size, name, sep='_')

  apply(examples, 1, make_example)
  
  
}
