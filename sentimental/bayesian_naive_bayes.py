# -*- coding: utf-8 -*-

import numpy as np

from sklearn.naive_bayes import BaseDiscreteNB
from sklearn.utils import atleast2d_or_csr
from sklearn.utils.extmath import safe_sparse_dot


class BernoulliBNB(BaseDiscreteNB):
    """Bayesian version of the Bernoulli Naive Bayes model.

    \pi         ~ Dir(\mathbf{\alpha})
    \theta_{jc} ~ Beta(\beta_0, \beta_1)

    :param prior_alpha: prior parameters of the mixing coefficients.
    :param prior_beta: prior parameters for feature probabilities.
    """
    def __init__(self, prior_alpha=1., prior_beta=np.array([1., 1.])):
        # we'll compute it from the sample.
        self.class_prior = None

        self.prior_alpha_ = prior_alpha
        self.prior_beta_ = prior_beta

    def _count(self, X, Y):
        """Count and smooth feature occurrences."""
        self.feature_count_ += safe_sparse_dot(Y.T, X)
        self.class_count_ += Y.sum(axis=0)

    def _update_class_log_prior(self, class_prior=None):
        """Apply smoothing to raw counts and recompute log prior probabilities."""
        smoothed_cc = self.class_count_ + self.prior_alpha_
        smoothed_tc = self.class_count_.sum() * self.prior_alpha_
        self.class_log_prior_ = np.log(smoothed_cc) - np.log(smoothed_tc)

    def _update_feature_log_prob(self):
        """Apply smoothing to raw counts and recompute log probabilities"""
        smoothed_fc = self.feature_count_ + self.prior_beta_[1]
        smoothed_cc = self.class_count_ + self.prior_beta_.sum()

        self.feature_log_prob_ = (np.log(smoothed_fc)
                                  - np.log(smoothed_cc.reshape(-1, 1)))

    def _joint_log_likelihood(self, X):
        """Calculate the posterior log probability of the samples X"""
        X = atleast2d_or_csr(X)
        neg_prob = np.log(1 - np.exp(self.feature_log_prob_))
        jll = safe_sparse_dot(X, (self.feature_log_prob_ - neg_prob).T)
        jll += self.class_log_prior_ + neg_prob.sum(axis=1)
        return jll
