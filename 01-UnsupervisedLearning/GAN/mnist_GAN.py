"""
  author: Sierkinhane
  since: 2019-11-7 19:29:06
  description: this code was based on GAN in actions(https://github.com/GANs-in-Action/gans-in-action)
"""
import torch
import torch.nn as nn
import mnist
import numpy as np
import torch.nn.functional as F
from collections import OrderedDict
import matplotlib.pyplot as plt
import math

# 1. generator
def build_generator():

	model = nn.Sequential(
		nn.Linear(100, 128),
		nn.ReLU(),
		nn.Linear(128, 28*28*1),
		nn.Sigmoid()
		)

	return model

# 2. discriminator
def build_discriminator():

	model = nn.Sequential(
		nn.Linear(28*28*1, 128),
		nn.ReLU(),
		nn.Linear(128, 1),
		nn.Sigmoid())

	return model

def sample_images(generator, iteration, device, image_grid_rows=4, image_grid_columns=4):

	# Sample random noise
	z = torch.from_numpy(np.random.normal(0, 1, (image_grid_rows*image_grid_columns, 100)).astype(np.float32)).to(device)

	# Generate images from random noise
	gen_imgs = generator(z).cpu().detach().numpy().reshape(-1, 28, 28)

	# Rescale image pixel values to [0, 1]
	# gen_imgs = 0.5 * gen_imgs + 0.5

	# Set image grid
	fig, axs = plt.subplots(image_grid_rows,
							image_grid_columns,
							figsize=(4, 4),
							sharey=True,
							sharex=True)

	cnt = 0
	for i in range(image_grid_rows):
		for j in range(image_grid_columns):
			# Output a grid of images
			axs[i, j].imshow(gen_imgs[cnt, :, :], cmap='gray')
			axs[i, j].axis('off')
			plt.savefig(str(iteration+1)+'_generated.jpg')
			cnt += 1

# 3. training
def train(generator, discriminator, device, iterations, batch_size, sample_interval, lr):

	generator.to(device)
	discriminator.to(device)

	# load the mnist dataset
	(X_train, _), (_, _) = mnist.load_data()

	# rescale [0, 255] graysacle pixel values to [-1. 1]
	X_train = X_train / 255.0
	X_train = np.expand_dims(X_train, axis=3)

	# labels for real and fake images
	real = torch.from_numpy(np.ones((batch_size, 1), dtype=np.float32)).to(device)
	fake = torch.from_numpy(np.zeros((batch_size, 1), dtype=np.float32)).to(device)

	# define optimizer 
	optimizer_G = torch.optim.Adam(params=generator.parameters(), lr=lr)
	optimizer_D = torch.optim.Adam(params=discriminator.parameters(), lr=lr)
	
	for iteration in range(iterations):

		# train the discriminator
		idx = np.random.randint(0, X_train.shape[0], batch_size)
		imgs = X_train[idx].astype(np.float32)

		imgs_t = torch.from_numpy(imgs).reshape(-1, 28*28).to(device)

		z = torch.from_numpy(np.random.normal(0, 1, (batch_size, 100)).astype(np.float32)).to(device)
		gen_imgs = generator(z)

		d_scores_real = discriminator(imgs_t)
		d_scores_fake = discriminator(gen_imgs)
		
		# you can choose this loss function
		# d_loss_real = F.binary_cross_entropy_with_logits(d_scores_real, real)
		# d_loss_fake = F.binary_cross_entropy_with_logits(d_scores_fake, fake)
		# d_loss = 0.5*torch.add(d_loss_real, d_loss_fake)

		# or consistent with Goodfellow
		d_loss = -torch.mean(torch.log(d_scores_real) + torch.log(1. - d_scores_fake))

		optimizer_D.zero_grad()
		d_loss.backward()
		optimizer_D.step()

		
		#train generator
		z = torch.from_numpy(np.random.normal(0, 1, (batch_size, 100)).astype(np.float32)).to(device)
		gen_imgs = generator(z)
		g_scores_real = discriminator(gen_imgs)

		# you can choose this loss function
		# g_loss = F.binary_cross_entropy_with_logits(g_scores_real, real)

		# or consistent with Goodfellow
		g_loss = -torch.mean(torch.log(g_scores_real))
		# g_loss = torch.mean(torch.log(1. - g_scores_real))

		optimizer_G.zero_grad()
		g_loss.backward()
		optimizer_G.step()

		if (iteration + 1) % sample_interval == 0:

			# Output training progress
			print("iteration {0}, d_loss {1:.4f},  g_loss {2:.4f}".format(iteration+1, d_loss, g_loss))

			# Output a sample of generated image
			sample_images(generator, iteration, device)

if __name__ == '__main__':
	
	iterations = 100000
	lr = 0.001
	batch_size = 128
	sample_interval = 1000

	device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
	generator = build_generator()
	discriminator = build_discriminator()

	train(generator, discriminator, device, iterations, batch_size, sample_interval, lr)
