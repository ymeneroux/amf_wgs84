# ------------------------------------------------------------------------
# Code pour le caclul de mélange gaussien par l'algorithme 
# expectation-maximization en 2D
# ------------------------------------------------------------------------

COLORS = matrix(c(
		1, 0, 0,
		0, 0, 1, 
		0, 0.5, 0,
		0.5, 0, 0,
		0, 0, 0.5,
		0, 1, 1,
		1, 0, 0,
		1, 0, 1,
		0, 0.5, 1,
		1, 0.5, 0,
		0.5,1,0), nrow=11, byrow=TRUE)


# set.seed(66348)     # Exemple avec convergence longue
# set.seed(71186)     # Exemple avec mauvais départ
# set.seed(26287)     # Exemple avec mauvaise solution

# ------------------------------------------------------------------------
# Fonction principale
# ------------------------------------------------------------------------
# Inputs: 
#    - data     : un data frame de n points (X,Y)
#    - k        : le nombre de classes à estimer
#    - epsilon  : critère de convergence (defaut : 0.0001)
#    - iter_max : nombre maximal d'itérations (defaut 100)
#    - verbose  : impression console
#    - plt      : affichage demo sous forme de plot
#    - pause    : delai en sec entre les images pour le plot
# Outputs:
#    - 1 objet contenant les attributs :
# 		- mean_X  : un vecteur de k moyennes sur X
# 		- mean_Y  : un vecteur de k moyennes sur Y
#       - std_x   : un vecteur de k écarts-types sur X
#       - std_y   : un vecteur de k écarts-types sur Y
#       - cov_xy  : un vecteyr de k covariances sur (X,Y)
#       - probas  : un data frame n x k des probas d'affectation
#       - cluster : un vecteur de n valeurs dans {1,2,...k)
# ------------------------------------------------------------------------
em = function(data, k, epsilon = 1e-4, iter_max = 100, verbose = TRUE, plt = FALSE, pause = 2){

	# ---------------------------------------------
	# Calibration
	# ---------------------------------------------
	mx = min(data[,1])
	my = min(data[,2])
	Mx = max(data[,1])
	My = max(data[,2])
	
	# ---------------------------------------------
	# Initialisation
	# ---------------------------------------------
	means_x = runif(k, mx, Mx);
	means_y = runif(k, my, My);
	std_x   = 0.5*runif(k, 0, Mx-mx);
	std_y   = 0.5*runif(k, 0, My-my);
	cov_xy  = runif(k, -0.5, 0.5)*std_x*std_y; 
	
	output = list(means_x = means_x, 
				  means_y = means_y, 
				  std_x   = std_x, 
				  std_y   = std_y, 
				  cov_xy  = cov_xy)
	
	# ---------------------------------------------
	# Itérations
	# ---------------------------------------------
	for (iter in 1:iter_max){
		
		# Affectations points
		probas = assignment(data, output)
		
		change = 0  # Modification à chaque itération
		
		# Calcul centres
		for (i in 1:ncol(probas)){
			Z = sum(probas[,i])
			mx_temp     = sum(probas[,i]*data[,1])/Z
			my_temp     = sum(probas[,i]*data[,2])/Z
			std_x_temp  = sqrt(sum(probas[,i]*(data[,1]-output$means_x[i])^2)/Z)
			std_y_temp  = sqrt(sum(probas[,i]*(data[,2]-output$means_y[i])^2)/Z)
			cov_xy_temp = sum(probas[,i]*(data[,1]-output$means_x[i])*(data[,2]-output$means_y[i]))/Z
			
			change = change + (output$means_x[i] - mx_temp)^2
			change = change + (output$means_y[i] - my_temp)^2
			change = change + (output$std_x[i]   - std_x_temp)^2
			change = change + (output$std_y[i]   - std_y_temp)^2
			change = change + (output$cov_xy[i]  - cov_xy_temp)^2
			
			output$means_x[i] = mx_temp
			output$means_y[i] = my_temp
			output$std_x[i]   = std_x_temp
			output$std_y[i]   = std_y_temp
			output$cov_xy[i]  = cov_xy_temp
		}
		
		change = sqrt(change/5)
		
		if (verbose){
			cat(paste("ITERATION", iter, " RMSE = ", change, "\n"))
		}
			
		# Tracé graphique centres et affectations "soft"
		if (plt){
			plot(data$X, data$Y, xlim=c(mx, Mx), ylim=c(my,My))
			cr = rep(0, nrow(data))
			cg = rep(0, nrow(data))
			cb = rep(0, nrow(data))
			for (j in 1:length(output$means_x)){
				cr = cr + probas[,j]*COLORS[j,1] 
				cg = cg + probas[,j]*COLORS[j,2] 
				cb = cb + probas[,j]*COLORS[j,3] 
			}
			
			points(data[,1], data[,2], col = rgb(cr, cg, cb), pch=16)
			
			plot_estimation(output)
			Sys.sleep(pause)
		}
		
		if (change < epsilon){
			break
		}
	
	}
	
	if (verbose){
		cat("----------------------------------------------------\n")
		cat(paste("CONVERGENCE REACHED AFTER", iter, "ITERATIONS\n"))
		cat("----------------------------------------------------\n")
	}
	
	# Mise en forme sortie
	output$probas = probas
	output$cluster = apply(output$probas, 1, which.max)
	return(output)

}

# ------------------------------------------------------------------------
# Extraction du i-eme centre de classe sous forme de vecteur liste
# ------------------------------------------------------------------------
makeMeanVec = function(centers, i){
	means = c(centers$means_x[i], centers$means_y[i]);
	return(means)
}

# ------------------------------------------------------------------------
# Extraction de la matrice de covariance de la i-eme classe
# ------------------------------------------------------------------------
makeCovMat = function(centers, i){
	sigma = matrix(c(centers$std_x[i]^2, centers$cov_xy[i], 
				     centers$cov_xy[i] , centers$std_y[i]^2),  nrow = 2)
	return(sigma)
}

# ------------------------------------------------------------------------
# Conversion de la i-eme classe 2x2 en ellipse
# f : facteur d'echelle
# ------------------------------------------------------------------------
cluster2Ellipse = function(centers, i, f=1){
	M = makeMeanVec(centers, i)
	C = makeCovMat(centers, i)
	E = eigen(C)
	a = sqrt(E$values[1])
	b = sqrt(E$values[2])
	phi = atan(E$vectors[2,1]/E$vectors[1,1])
	t = seq(0, 2*pi, 0.01) 
	x = M[1] + f*(a*cos(t)*cos(phi) - b*sin(t)*sin(phi))
	y = M[2] + f*(a*cos(t)*sin(phi) + b*sin(t)*cos(phi))
	return(data.frame(x, y))
}

# ------------------------------------------------------------------------
# Affectation de probabilités à chaque point pour chaque classe
# ------------------------------------------------------------------------
assignment = function(data, centers){
	output = data.frame(rep(0, nrow(data)));
	for (j in 1:length(centers$means_x)){
		probas = rep(0, nrow(data))
		for (i in 1:nrow(data)){
			pti = c(data[i,1], data[i,2])
			D = dmvnorm(pti, makeMeanVec(centers, j),  makeCovMat(centers, j))
			Z = 0
			for (k in 1:length(centers$means_x)){
				Z = Z + dmvnorm(pti, makeMeanVec(centers, k),  makeCovMat(centers, k))
			}
			probas[i] = D/as.numeric(Z)
		}
		output = cbind(output, probas)
	}
	output = output[,2:ncol(output)]
	return(output)
}

# ------------------------------------------------------------------------
# Tracé graphique des ellipses de classes
# ------------------------------------------------------------------------
plot_estimation = function(centers){
	for (i in 1:length(centers$means_x)){
		color = rgb(COLORS[i,1], COLORS[i,2], COLORS[i,3])
		for (f in seq(0.1, sqrt(5.991), 0.5)){
			ellipse = cluster2Ellipse(centers, i, f)
			lines(ellipse$x, ellipse$y, col=color, lty=2)
		}
	}
}

# ------------------------------------------------------------------------
#  Calcul de la densité de la loi normale multivariée en 1 point
# ------------------------------------------------------------------------
dmvnorm = function(x, means, covariance){
	K = length(x)
	X = matrix(x, nrow=K)
	M = matrix(means, nrow=K)
	arg = -0.5*t(X-M) %*% solve(covariance) %*% (X-M)
	return(1/sqrt((2*pi)^K*det(covariance)) * exp(arg))
}