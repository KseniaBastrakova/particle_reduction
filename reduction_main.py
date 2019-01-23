from shutil import copyfile
import read_hdf_file
import argparse
import Voronoi_algorithm
import os
import h5py
import Random_thinning_algorithm


def voronoi_reduction(hdf_file, hdf_file_reduction, tolerance_momentum, tolerance_position):
    """ Create name of reducted file, array of momentum """

    name_hdf_file_reduction = ''

    if hdf_file != '':
        if os.path.exists(hdf_file):
            name = hdf_file[:-4]
            idx_of_name = name.rfind('/')
            if idx_of_name != -1:
                name_hdf_file_reduction = hdf_file_reduction + hdf_file[idx_of_name + 1: -6] + 'reduction.h5'
            else:
                name_hdf_file_reduction = hdf_file_reduction + hdf_file[:-3] + '.h5'

            tolerances = [tolerance_momentum, tolerance_position]
            voronoi_algorithm(hdf_file, hdf_file_reduction, tolerances)
        else:
            print('The .hdf file does not exist')


def voronoi_algorithm(hdf_file_name, hdf_file_reduction_name, tolerances):
    """ Create copy of  original file, iterate base groups"""

    copyfile(hdf_file_name, hdf_file_reduction_name)

    hdf_file = h5py.File(hdf_file_name, 'a')
    hdf_file_reduction = h5py.File(hdf_file_reduction_name, 'a')
    particles_name = read_hdf_file.get_particles_name(hdf_file_reduction)

    particles_collect = read_hdf_file.ParticlesGroups(particles_name)
    hdf_file.visititems(particles_collect)
    for group in particles_collect.particles_groups:

        points = read_hdf_file.read_group_values(group)
        result = Voronoi_algorithm.run_algorithm(points, tolerances)
        point_converter = read_hdf_file.CoverterVoronoiToPoints(result)
        library_datasets = read_hdf_file.create_library_of_datasets(point_converter.points)

        read_hdf_file.write_group_values(hdf_file_reduction, group, library_datasets)
def random_thinning_algorithm(hdf_file_name, hdf_file_reduction_name, reduction_percent):

    copyfile(hdf_file_name, hdf_file_reduction_name)
    hdf_file = h5py.File(hdf_file_name, 'a')
    hdf_file_reduction = h5py.File(hdf_file_reduction_name, 'a')
    particles_name = read_hdf_file.get_particles_name(hdf_file_reduction)
    particles_collect = read_hdf_file.ParticlesGroups(particles_name)
    hdf_file.visititems(particles_collect)

    for group in particles_collect.particles_groups:
        points = read_hdf_file.read_group_values(group)
        num_particles, num_particles_offset = read_hdf_file.read_patches_values(group)
        parameters = Random_thinning_algorithm.RandomThinningAlgorithmParameters(reduction_percent, num_particles, num_particles_offset)
        algorithm = Random_thinning_algorithm.RandomThinningAlgorithm(parameters)
        result, num_particles_offset, num_particles = algorithm.run(points)
        library_datasets = read_hdf_file.create_library_of_datasets(result)
        read_hdf_file.write_group_values(hdf_file_reduction, group, library_datasets, num_particles_offset,
                                         num_particles)


if __name__ == "__main__":
    """ Parse arguments from command line """

    parser = argparse.ArgumentParser(description="voronoi reduction")

    parser.add_argument("-algorithm", metavar='algorithm', type=str,
                        help="hdf file without patches")

    parser.add_argument("-hdf", metavar='hdf_file', type=str,
                        help="hdf file without patches")

    parser.add_argument("-hdf_re", metavar='hdf_file_reduction', type=str,
                        help="reducted hdf file")

    parser.add_argument("-reduction_percent", metavar='reduction_percent', type=float,
                        help="part of the particles to reduce")

    parser.add_argument("-momentum_tol", metavar='tolerance_momentum', type=float,
                        help="tolerance of momentum")

    parser.add_argument("-momentum_pos", metavar='tolerance_position', type=float,
                        help="tolerance of position")

    args = parser.parse_args()

    if args.algorithm == 'voronoi':
        voronoi_reduction(args.hdf, args.hdf_re, args.momentum_tol, args.momentum_pos)
    elif args.algorithm == 'random':
        random_thinning_algorithm()


