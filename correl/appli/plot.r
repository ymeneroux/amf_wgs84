targets = c("50", "51", "52", "53", "54", "55", "56", "G2", "S33")

for (i in 1:length(targets)){
	pdf(paste(targets[i], ".pdf", sep=''))
	par(mfrow=c(2,1))
	data = read.csv(paste("Out_correl/csv/",targets[i],".csv", sep=''))
	plot(data$x, type='l', col='blue', ylab="x (px)")
	plot(data$y, type='l', col='red' , ylab="y (px)", xlab=paste("Tracking of target #", targets[1], sep=''))
	dev.off()
	cat(paste("Plot for target #", targets[i], " ok\n"))
}

